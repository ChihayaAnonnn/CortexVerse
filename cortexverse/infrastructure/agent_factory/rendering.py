"""Prompt 渲染引擎 — ${var} 占位、缺失熔断、对象自动序列化。"""

import json
from string import Template
from typing import Any

from pydantic import BaseModel


def _to_text(value: Any) -> str:
    """将上下文值统一序列化为字符串。"""
    if isinstance(value, str):
        return value
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    return json.dumps(value, ensure_ascii=False)


def render_prompt(prompt_lines: list[str], context: dict[str, Any]) -> str:
    """合并模板行并渲染 ${var} 变量。

    Args:
        prompt_lines: Prompt 模板行列表。
        context: 渲染上下文；非字符串值将被自动序列化。

    Returns:
        渲染后的完整 prompt 字符串。

    Raises:
        ValueError: 当缺失必须的上下文变量时。
    """
    raw_text = "\n".join(prompt_lines).strip()
    safe_context = {key: _to_text(val) for key, val in context.items()}
    try:
        # substitute 在缺失变量时抛 KeyError，实现严格熔断
        return Template(raw_text).substitute(safe_context)
    except KeyError as exc:
        raise ValueError(f"提示词渲染失败：缺失必须的上下文变量 {exc}") from exc
