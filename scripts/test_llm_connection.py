"""LLM provider 连通性测试脚本。"""

from __future__ import annotations

import argparse
import asyncio
import sys

from pydantic import BaseModel, Field

from cortexverse.infrastructure.llm_clients.factory import LLMClientFactory

_DEFAULT_MODELS: dict[str, str] = {
    "deepseek": "deepseek-chat",
    "openai": "gpt-4o-mini",
}


class _PingResponse(BaseModel):
    """连通性测试用的最小结构化响应。"""

    reply: str = Field(description="对用户问题的简短回复")


async def _run(provider: str, model: str, prompt: str) -> None:
    """向指定 provider 发送测试请求并打印响应。"""
    factory = LLMClientFactory.from_config()
    client = factory.get_client(provider)
    result = await client.chat.completions.create(
        model=model,
        response_model=_PingResponse,
        max_retries=0,
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"✅ [{provider}] 连接成功: {result.reply}")


def main() -> int:
    """解析 CLI 参数并执行连通性测试。"""
    parser = argparse.ArgumentParser(description="测试 LLM provider 连通性")
    parser.add_argument(
        "--provider",
        default="deepseek",
        help="llm_providers.yaml 中的 provider 名称（默认: deepseek）",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="模型名称（默认按 provider 自动选择）",
    )
    parser.add_argument(
        "--prompt",
        default="说一个字",
        help="测试用 user prompt",
    )
    args = parser.parse_args()
    model = args.model or _DEFAULT_MODELS.get(args.provider, "deepseek-chat")

    try:
        asyncio.run(_run(args.provider, model, args.prompt))
    except EnvironmentError as exc:
        print(f"❌ 环境变量未配置: {exc}", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as exc:
        print(f"❌ 配置错误: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — CLI 脚本需捕获并展示底层 SDK 错误
        print(f"❌ 请求失败: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
