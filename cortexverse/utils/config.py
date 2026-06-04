"""全局配置管理器 — 单例模式，统一读取和管理环境变量。"""

import os
from typing import Any

from loguru import logger


class ConfigManager:
    """全局配置管理器（单例模式）。

    提供统一的环境变量读取接口，支持：
    - LLM Provider 配置（API Key、Base URL）
    - 数据库连接配置
    - Redis 连接配置
    - 其他业务配置

    使用方式：
        from cortexverse.utils.config import ConfigManager
        config = ConfigManager()
        api_key = config.OPENAI_API_KEY
    """

    _instance: "ConfigManager | None" = None
    _initialized: bool = False

    def __new__(cls) -> "ConfigManager":
        """确保单例模式。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初始化配置管理器。"""
        if ConfigManager._initialized:
            return
        ConfigManager._initialized = True

        # ==========================================
        # LLM Provider 配置
        # ==========================================
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        self.DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        # ==========================================
        # 数据库配置
        # ==========================================
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "")

        # ==========================================
        # Redis 配置
        # ==========================================
        self.REDIS_URL: str = os.getenv("REDIS_URL", "")

        # ==========================================
        # 业务配置
        # ==========================================
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

        # LLM Provider 配置映射（供 LLMClientFactory 使用）
        self._llm_providers: dict[str, dict[str, str]] = {
            "openai": {
                "type": "openai",
                "base_url": self.OPENAI_BASE_URL,
                "api_key_env": "OPENAI_API_KEY",
            },
            "deepseek": {
                "type": "openai",
                "base_url": self.DEEPSEEK_BASE_URL,
                "api_key_env": "DEEPSEEK_API_KEY",
            },
        }

        logger.info("ConfigManager 初始化完成")

    def get(self, key: str, default: Any = None) -> Any:
        """获取环境变量。

        Args:
            key: 环境变量名。
            default: 默认值。

        Returns:
            环境变量值或默认值。
        """
        return os.getenv(key, default)

    def get_required(self, key: str) -> str:
        """获取必需的环境变量。

        Args:
            key: 环境变量名。

        Returns:
            环境变量值。

        Raises:
            ValueError: 环境变量未设置。
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"必需的环境变量 `{key}` 未设置")
        return value

    def get_llm_providers(self) -> dict[str, dict[str, str]]:
        """获取所有 LLM Provider 配置。

        Returns:
            Provider 配置字典。
        """
        return self._llm_providers.copy()

    def get_llm_provider(self, provider_name: str) -> dict[str, str]:
        """获取指定 LLM Provider 配置。

        Args:
            provider_name: Provider 名称。

        Returns:
            Provider 配置。

        Raises:
            ValueError: Provider 不存在。
        """
        if provider_name not in self._llm_providers:
            raise ValueError(f"LLM Provider `{provider_name}` 未配置")
        return self._llm_providers[provider_name].copy()

    def get_api_key(self, provider_name: str) -> str:
        """获取 LLM Provider 的 API Key。

        Args:
            provider_name: Provider 名称。

        Returns:
            API Key。

        Raises:
            ValueError: Provider 不存在或 API Key 未设置。
        """
        provider = self.get_llm_provider(provider_name)
        api_key_env = provider["api_key_env"]
        return self.get_required(api_key_env)

    def reload(self) -> None:
        """重新加载配置（支持热更新）。"""
        ConfigManager._initialized = False
        self.__init__()
        logger.info("ConfigManager 配置已重新加载")


# 全局单例实例
config = ConfigManager()
