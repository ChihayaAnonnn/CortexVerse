"""LLM 客户端工厂 — 基于 provider 配置创建 instructor 客户端。"""

from pathlib import Path
from typing import Any

import instructor
import yaml

from cortexverse.infrastructure.llm_clients.base import BaseLLMClient
from cortexverse.infrastructure.llm_clients.openai_client import OpenAICompatibleClient

_DEFAULT_PROVIDERS_PATH = Path(__file__).resolve().parents[3] / "configs" / "llm_providers.yaml"

# provider type → 客户端类映射
_CLIENT_TYPES: dict[str, type[BaseLLMClient]] = {
    "openai": OpenAICompatibleClient,
}


class LLMClientFactory:
    """LLM 客户端工厂。根据 provider 名称创建 instructor 客户端。

    缓存已创建的客户端实例，避免重复创建 SDK 连接。
    """

    def __init__(self, providers: dict[str, Any]) -> None:
        self._providers = providers
        self._cache: dict[str, instructor.AsyncInstructor] = {}

    @classmethod
    def from_config(cls, config_path: str | Path | None = None) -> "LLMClientFactory":
        """加载 llm_providers.yaml 配置。

        Args:
            config_path: 配置文件路径；默认使用包内锚定路径。

        Returns:
            就绪的 LLMClientFactory 实例。
        """
        path = Path(config_path) if config_path else _DEFAULT_PROVIDERS_PATH
        with open(path, "r", encoding="utf-8") as fp:
            providers: dict[str, Any] = yaml.safe_load(fp)
        return cls(providers)

    def get_client(self, provider_name: str) -> instructor.AsyncInstructor:
        """根据 provider 名称获取或创建 instructor 客户端。

        Args:
            provider_name: llm_providers.yaml 中的 provider 键名。

        Returns:
            instructor.AsyncInstructor 客户端实例。

        Raises:
            ValueError: provider 未在配置中定义。
            KeyError: provider type 不受支持。
        """
        if provider_name in self._cache:
            return self._cache[provider_name]

        if provider_name not in self._providers:
            raise ValueError(f"Provider 配置错误：未找到 provider `{provider_name}`")

        spec = self._providers[provider_name]
        provider_type = spec["type"]

        client_class = _CLIENT_TYPES.get(provider_type)
        if client_class is None:
            raise KeyError(
                f"不支持的 provider type `{provider_type}`；"
                f"可用类型：{list(_CLIENT_TYPES.keys())}"
            )

        client = client_class(
            base_url=spec["base_url"],
            api_key_env=spec["api_key_env"],
            provider_name=provider_name,
        )
        instructor_client = client.create_client()
        self._cache[provider_name] = instructor_client
        return instructor_client
