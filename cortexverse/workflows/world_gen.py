"""世界构建编排器 — 四阶段流水线，每阶段含独立 refine 循环。"""

import uuid

from loguru import logger
from pydantic import ValidationError

from cortexverse.agents import _schema_bindings  # noqa: F401
from cortexverse.domain.macro import MacroState
from cortexverse.domain.micro import ConflictState, EconomyState, GeographyState
from cortexverse.domain.world_asset import WorldAsset
from cortexverse.infrastructure.agent_factory.factory import AgentFactory

MAX_REFINE = 3


async def _run_with_refine(
    agent_name: str,
    template: str,
    context: dict,
    factory: AgentFactory,
) -> any:
    """执行单个 agent，含 refine 循环。"""
    agent = factory.create_agent(agent_name)
    current_template = template

    for attempt in range(MAX_REFINE):
        logger.info("[{}] 第 {} 次尝试 template={}", agent_name, attempt + 1, current_template)
        result = await agent.run(current_template, **context)
        return result

    raise RuntimeError(f"Agent `{agent_name}` 在最大 refine 次数内仍未完成")


async def run_world_generation(
    world_name: str,
    genre_tags: list[str],
    theme_input: str,
) -> WorldAsset:
    """执行四阶段世界构建流水线。

    阶段：
    1. macro_architect → MacroState
    2. geography_subagent → GeographyState
    3. economy_subagent → EconomyState
    4. conflict_subagent → ConflictState

    Args:
        world_name: 世界名称。
        genre_tags: 题材标签列表。
        theme_input: 核心主题倾向。

    Returns:
        组装完成的 WorldAsset。
    """
    factory = AgentFactory.from_config()
    world_id = f"world_{uuid.uuid4().hex[:8]}"

    # ── 阶段 1：宏观架构 ──────────────────────────────────────────
    logger.info("阶段 1/4：宏观架构师")
    macro_state: MacroState = await _run_with_refine(
        "macro_architect",
        "generate",
        {"world_name": world_name, "theme_input": theme_input, "genre_tags": ", ".join(genre_tags)},
        factory,
    )

    # ── 阶段 2：地理精算 ──────────────────────────────────────────
    logger.info("阶段 2/4：地理精算师")
    geography_state: GeographyState = await _run_with_refine(
        "geography_subagent",
        "generate",
        {"macro_context": macro_state.model_dump_json()},
        factory,
    )

    # ── 阶段 3：经济社会 ──────────────────────────────────────────
    logger.info("阶段 3/4：阶级与社会精算师")
    economy_state: EconomyState = await _run_with_refine(
        "economy_subagent",
        "generate",
        {
            "macro_context": macro_state.model_dump_json(),
            "geography_context": geography_state.model_dump_json(),
        },
        factory,
    )

    # ── 阶段 4：冲突编排 ──────────────────────────────────────────
    logger.info("阶段 4/4：冲突编排师")
    conflict_state: ConflictState = await _run_with_refine(
        "conflict_subagent",
        "generate",
        {
            "macro_context": macro_state.model_dump_json(),
            "geography_context": geography_state.model_dump_json(),
            "economy_context": economy_state.model_dump_json(),
        },
        factory,
    )

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
