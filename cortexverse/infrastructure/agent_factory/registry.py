"""Agent 输出 Schema 注册表 — 单一事实源。"""

from typing import Any

from pydantic import BaseModel

# 配置 Key → 响应模型（Model 或 list[Model]）
SCHEMA_REGISTRY: dict[str, Any] = {}


def register_schema(agent_key: str, *, many: bool = False):
    """将 Pydantic 模型注册到指定 agent_key。

    Args:
        agent_key: 与 agents.yaml 中的节点 Key 对应。
        many: 为 True 时产出形态为 list[Model]，用于产出原子节点列表的 SubAgent。

    Returns:
        类装饰器；不改变被装饰类本身。
    """

    def decorator(model: type[BaseModel]) -> type[BaseModel]:
        SCHEMA_REGISTRY[agent_key] = list[model] if many else model
        return model

    return decorator
