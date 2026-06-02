"""LLMClientFactory 测试。"""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from cortexverse.infrastructure.llm_clients.factory import LLMClientFactory


class TestLLMClientFactory:
    """LLMClientFactory 的单元测试。"""

    def test_from_config_loads_providers(self, tmp_path: Path) -> None:
        """验证 YAML 配置正确加载。"""
        config = {
            "test_provider": {
                "type": "openai",
                "base_url": "https://api.test.com/v1",
                "api_key_env": "TEST_API_KEY",
            }
        }
        config_path = tmp_path / "providers.yaml"
        config_path.write_text(yaml.dump(config), encoding="utf-8")

        factory = LLMClientFactory.from_config(config_path)
        assert factory._providers == config

    def test_get_client_raises_on_unknown_provider(self, tmp_path: Path) -> None:
        """验证未知 provider 名称抛出 ValueError。"""
        config_path = tmp_path / "providers.yaml"
        config_path.write_text(yaml.dump({}), encoding="utf-8")

        factory = LLMClientFactory.from_config(config_path)
        with pytest.raises(ValueError, match="未找到 provider"):
            factory.get_client("nonexistent")

    def test_get_client_raises_on_unsupported_type(self, tmp_path: Path) -> None:
        """验证不支持的 provider type 抛出 KeyError。"""
        config = {
            "bad_provider": {
                "type": "unsupported_type",
                "base_url": "https://api.test.com/v1",
                "api_key_env": "TEST_API_KEY",
            }
        }
        config_path = tmp_path / "providers.yaml"
        config_path.write_text(yaml.dump(config), encoding="utf-8")

        factory = LLMClientFactory.from_config(config_path)
        with pytest.raises(KeyError, match="不支持的 provider type"):
            factory.get_client("bad_provider")

    @patch.dict("os.environ", {"TEST_API_KEY": "sk-test"})
    def test_get_client_caches_instances(self, tmp_path: Path) -> None:
        """验证相同 provider 返回缓存的客户端实例。"""
        config = {
            "test_provider": {
                "type": "openai",
                "base_url": "https://api.test.com/v1",
                "api_key_env": "TEST_API_KEY",
            }
        }
        config_path = tmp_path / "providers.yaml"
        config_path.write_text(yaml.dump(config), encoding="utf-8")

        factory = LLMClientFactory.from_config(config_path)
        client1 = factory.get_client("test_provider")
        client2 = factory.get_client("test_provider")
        assert client1 is client2

    def test_from_config_raises_on_missing_file(self) -> None:
        """验证配置文件不存在时抛出异常。"""
        with pytest.raises(FileNotFoundError):
            LLMClientFactory.from_config("/nonexistent/path.yaml")
