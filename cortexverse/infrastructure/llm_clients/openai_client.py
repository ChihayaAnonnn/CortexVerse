"""OpenAI 兼容 LLM 客户端（覆盖 OpenAI、DeepSeek 等）。"""

import os

import instructor
import openai

from cortexverse.infrastructure.llm_clients.base import BaseLLMClient


class OpenAICompatibleClient(BaseLLMClient):
    """OpenAI 兼容客户端。支持所有 OpenAI SDK 兼容的 provider。

    Args:
        base_url: API 端点地址。
        api_key_env: 环境变量名，从中读取 API Key。
        provider_name: provider 标识名称。
    """

    def __init__(self, base_url: str, api_key_env: str, provider_name: str = "openai") -> None:
        self._base_url = base_url
        self._api_key_env = api_key_env
        self._provider_name = provider_name

    def create_client(self) -> instructor.AsyncInstructor:
        """创建 OpenAI AsyncOpenAI 实例并用 instructor 包装。"""
        api_key = os.environ.get(self._api_key_env)
        if not api_key:
            raise EnvironmentError(
                f"环境变量 {self._api_key_env} 未设置，无法创建 {self._provider_name} 客户端"
            )
        native_client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=self._base_url,
        )
        return instructor.from_openai(native_client)

    @property
    def provider_name(self) -> str:
        return self._provider_name
