"""Prompt 渲染引擎测试。"""

import pytest
from pydantic import BaseModel

from cortexverse.infrastructure.agent_factory.rendering import render_prompt


def test_render_prompt_with_string_vars() -> None:
    """测试字符串变量渲染。"""
    lines = ["题材：${genre}", "意图：${intent}"]
    result = render_prompt(lines, {"genre": "赛博朋克", "intent": "末世生存"})
    assert result == "题材：赛博朋克\n意图：末世生存"


def test_render_prompt_with_pydantic_model() -> None:
    """测试 Pydantic 模型自动序列化。"""

    class MockModel(BaseModel):
        name: str
        value: int

    lines = ["数据：${data}"]
    result = render_prompt(lines, {"data": MockModel(name="test", value=42)})
    assert '"name":"test"' in result
    assert '"value":42' in result


def test_render_prompt_missing_var_raises_error() -> None:
    """测试缺失变量时抛出 ValueError。"""
    lines = ["题材：${genre}", "意图：${intent}"]
    with pytest.raises(ValueError, match="提示词渲染失败"):
        render_prompt(lines, {"genre": "赛博朋克"})


def test_render_prompt_with_literal_dollar() -> None:
    """测试字面量 $ 使用 $$ 转义。"""
    lines = ["价格：$$100"]
    result = render_prompt(lines, {})
    assert result == "价格：$100"
