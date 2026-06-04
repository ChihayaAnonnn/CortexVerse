"""LLM 客户端工厂 — 基于环境变量创建 instructor 客户端。"""

from typing import Any

import instructor

from cortexverse.infrastructure.llm_clients.base import BaseLLMClient
from cortexverse.infrastructure.llm_clients.openai_client import OpenAICompatibleClient
from cortexverse.utils.config import ConfigManager

# provider type → 客户端类映射
_CLIENT_TYPES: dict[str, type[BaseLLMClient]] = {
    "openai": OpenAICompatibleClient,
}


class LLMClientFactory:
    """LLM 客户端工厂。根据 provider 名称创建 instructor 客户端。

    从 ConfigManager 读取配置，缓存已创建的客户端实例，避免重复创建 SDK 连接。
    """

    def __init__(self, config_manager: ConfigManager) -> None:
        self._config_manager = config_manager
        self._cache: dict[str, instructor.AsyncInstructor] = {}

    @classmethod
    def from_config(cls) -> "LLMClientFactory":
        """从 ConfigManager 创建 LLMClientFactory。

        Returns:
            就绪的 LLMClientFactory 实例。
        """
        config_manager = ConfigManager()
        return cls(config_manager)

    def get_client(self, provider_name: str) -> instructor.AsyncInstructor:
        """根据 provider 名称获取或创建 instructor 客户端。

        Args:
            provider_name: Provider 名称（如 'openai', 'deepseek'）。

        Returns:
            instructor.AsyncInstructor 客户端实例。

        Raises:
            ValueError: provider 未在配置中定义。
            KeyError: provider type 不受支持。
        """
        if provider_name in self._cache:
            return self._cache[provider_name]

        provider = self._config_manager.get_llm_provider(provider_name)
        provider_type = provider["type"]

        client_class = _CLIENT_TYPES.get(provider_type)
        if client_class is None:
            raise KeyError(
                f"不支持的 provider type `{provider_type}`；"
                f"可用类型：{list(_CLIENT_TYPES.keys())}"
            )

        client = client_class(
            base_url=provider["base_url"],
            api_key_env=provider["api_key_env"],
            provider_name=provider_name,
        )
        instructor_client = client.create_client()
        self._cache[provider_name] = instructor_client
        return instructor_client
