"""Agent Schema 注册表测试。"""

from pydantic import BaseModel

from cortexverse.infrastructure.agent_factory.registry import SCHEMA_REGISTRY, register_schema


def test_register_schema_single() -> None:
    """测试单体模型注册。"""

    class MockModel(BaseModel):
        name: str

    # 清空注册表避免干扰
    original = SCHEMA_REGISTRY.copy()
    SCHEMA_REGISTRY.clear()

    try:
        register_schema("test_agent")(MockModel)
        assert "test_agent" in SCHEMA_REGISTRY
        assert SCHEMA_REGISTRY["test_agent"] is MockModel
    finally:
        SCHEMA_REGISTRY.clear()
        SCHEMA_REGISTRY.update(original)


def test_register_schema_many() -> None:
    """测试列表模型注册。"""

    class MockItem(BaseModel):
        id: str

    original = SCHEMA_REGISTRY.copy()
    SCHEMA_REGISTRY.clear()

    try:
        register_schema("test_list_agent", many=True)(MockItem)
        assert "test_list_agent" in SCHEMA_REGISTRY
        # many=True 时应为 list[MockItem]
        assert SCHEMA_REGISTRY["test_list_agent"] == list[MockItem]
    finally:
        SCHEMA_REGISTRY.clear()
        SCHEMA_REGISTRY.update(original)
