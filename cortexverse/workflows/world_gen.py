"""世界构建编排器 — 四阶段流水线，每阶段含独立 refine 循环。"""

import uuid
from collections.abc import Callable
from typing import Any

from loguru import logger
from pydantic import BaseModel

from cortexverse.agents import _schema_bindings  # noqa: F401
from cortexverse.domain.macro import MacroState
from cortexverse.domain.micro import ConflictState, EconomyState, GeographyState
from cortexverse.domain.world_asset import WorldAsset
from cortexverse.infrastructure.agent_factory.factory import AgentFactory

MAX_REFINE = 3

# 进度回调类型：阶段名、阶段序号、阶段结果
ProgressCallback = Callable[[str, int, BaseModel | None], None]


def _validate_conflict_refs(conflict_state: ConflictState, economy_state: EconomyState) -> list[str]:
    """校验冲突节点的外键引用是否合法。"""
    errors: list[str] = []
    faction_ids = {f.faction_id for f in economy_state.micro_factions}
    resource_ids = {r.resource_id for r in economy_state.micro_resources}

    for conflict in conflict_state.micro_conflicts:
        if conflict.faction_a_id not in faction_ids:
            errors.append(f"冲突 {conflict.conflict_id} 的 faction_a_id ({conflict.faction_a_id}) 不存在，可用势力：{faction_ids}")
        if conflict.faction_b_id not in faction_ids:
            errors.append(f"冲突 {conflict.conflict_id} 的 faction_b_id ({conflict.faction_b_id}) 不存在，可用势力：{faction_ids}")
        if conflict.contested_resource_id not in resource_ids:
            errors.append(f"冲突 {conflict.conflict_id} 的 contested_resource_id ({conflict.contested_resource_id}) 不存在，可用资源：{resource_ids}")

    return errors


async def _run_with_refine(
    agent_name: str,
    template: str,
    context: dict[str, Any],
    factory: AgentFactory,
    validator: Callable[[Any], list[str]] | None = None,
) -> Any:
    """执行单个 agent，含 refine 循环。"""
    agent = factory.create_agent(agent_name)
    current_template = template

    for attempt in range(MAX_REFINE):
        logger.info("[{}] 第 {} 次尝试 template={}", agent_name, attempt + 1, current_template)
        result = await agent.run(current_template, **context)

        if validator is not None:
            errors = validator(result)
            if errors:
                feedback = "\n".join(errors)
                logger.warning("[{}] 校验失败，尝试 refine：{}", agent_name, feedback)
                context["feedback"] = feedback
                current_template = "refine"
                continue

        return result

    raise RuntimeError(f"Agent `{agent_name}` 在最大 refine 次数内仍未完成")


async def run_world_generation(
    world_name: str,
    genre_tags: list[str],
    theme_input: str,
    on_progress: ProgressCallback | None = None,
) -> WorldAsset:
    """执行四阶段世界构建流水线。

    Args:
        world_name: 世界名称。
        genre_tags: 题材标签列表。
        theme_input: 核心主题倾向。
        on_progress: 进度回调，每阶段完成时调用。

    Returns:
        组装完成的 WorldAsset。
    """
    factory = AgentFactory.from_config()
    world_id = f"world_{uuid.uuid4().hex[:8]}"

    # ── 阶段 1：宏观架构 ──────────────────────────────────────────
    logger.info("阶段 1/4：宏观架构师")
    if on_progress:
        on_progress("macro_architect", 0, None)

    macro_state: MacroState = await _run_with_refine(
        "macro_architect",
        "generate",
        {"world_name": world_name, "theme_input": theme_input, "genre_tags": ", ".join(genre_tags)},
        factory,
    )

    if on_progress:
        on_progress("macro_architect", 1, macro_state)

    # ── 阶段 2：地理精算 ──────────────────────────────────────────
    logger.info("阶段 2/4：地理精算师")
    if on_progress:
        on_progress("geography_subagent", 1, None)

    geography_state: GeographyState = await _run_with_refine(
        "geography_subagent",
        "generate",
        {"macro_context": macro_state.model_dump_json()},
        factory,
    )

    if on_progress:
        on_progress("geography_subagent", 2, geography_state)

    # ── 阶段 3：经济社会 ──────────────────────────────────────────
    logger.info("阶段 3/4：阶级与社会精算师")
    if on_progress:
        on_progress("economy_subagent", 2, None)

    economy_state: EconomyState = await _run_with_refine(
        "economy_subagent",
        "generate",
        {
            "macro_context": macro_state.model_dump_json(),
            "geography_context": geography_state.model_dump_json(),
        },
        factory,
    )

    if on_progress:
        on_progress("economy_subagent", 3, economy_state)

    # ── 阶段 4：冲突编排（带外键校验） ──────────────────────────
    logger.info("阶段 4/4：冲突编排师")
    if on_progress:
        on_progress("conflict_subagent", 3, None)

    def conflict_validator(state: ConflictState) -> list[str]:
        return _validate_conflict_refs(state, economy_state)

    conflict_state: ConflictState = await _run_with_refine(
        "conflict_subagent",
        "generate",
        {
            "macro_context": macro_state.model_dump_json(),
            "geography_context": geography_state.model_dump_json(),
            "economy_context": economy_state.model_dump_json(),
        },
        factory,
        validator=conflict_validator,
    )

    if on_progress:
        on_progress("conflict_subagent", 4, conflict_state)

    # ── 组装 WorldAsset ──────────────────────────────────────────
    logger.info("组装 WorldAsset world_id={}", world_id)
    world_asset = WorldAsset(
        world_id=world_id,
        name=world_name,
        genre_tags=genre_tags,
        macro_philosophy=macro_state.macro_philosophy,
        macro_history=macro_state.macro_history,
        macro_growth=macro_state.macro_growth,
        micro_locations=geography_state.micro_locations,
        micro_hierarchy=economy_state.micro_hierarchy,
        micro_resources=economy_state.micro_resources,
        micro_factions=economy_state.micro_factions,
        micro_characters=economy_state.micro_characters,
        micro_conflicts=conflict_state.micro_conflicts,
    )

    logger.info("世界构建完成 world_id={}", world_id)
    return world_asset
