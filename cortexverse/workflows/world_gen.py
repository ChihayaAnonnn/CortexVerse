"""世界构建编排器 — 含关系校验驱动的 refine 循环。"""

from pydantic import ValidationError

# 确保 Schema 注册表在工厂断言前完成加载
from cortexverse.agents import _schema_bindings  # noqa: F401
from cortexverse.domain.world_asset import WorldAsset
from cortexverse.infrastructure.agent_factory.factory import AgentFactory

MAX_REFINE = 3


async def run_world_generation(genre_tags: list[str], creative_intent: str) -> WorldAsset:
    """执行世界构建流水线。

    Args:
        genre_tags: 题材标签列表。
        creative_intent: 创作意图。

    Returns:
        通过关系校验的世界观资产。
    """
    factory = AgentFactory.from_config()
    agent = factory.create_agent("world_builder")

    context: dict = {"genre_tags": genre_tags, "creative_intent": creative_intent}
    template = "generate_world"

    for _ in range(MAX_REFINE):
        candidate = await agent.run(template, **context)
        try:
            # WorldAsset 的 model_validator 在此触发企业级关系校验
            return WorldAsset.model_validate(candidate)
        except ValidationError as exc:
            # 关系级失败 instructor 修不了，交由编排层用 refine 模板重调
            context["feedback"] = str(exc)
            template = "refine_world"

    raise RuntimeError("世界构建在最大 refine 次数内仍未通过关系校验")
