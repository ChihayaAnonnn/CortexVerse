"""AgentFactory 测试。"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from cortexverse.infrastructure.agent_factory.factory import AgentFactory
from cortexverse.infrastructure.agent_factory.registry import SCHEMA_REGISTRY
from cortexverse.infrastructure.llm_clients.factory import LLMClientFactory


# ── 常量 ──────────────────────────────────────────────────────────────────────
_VALID_CONFIG = Path(__file__).resolve().parents[2] / "config" / "agents.yaml"
_MINIMAL_CONFIG = {
    "world_builder": {
        "provider": "openai",
        "model": "gpt-4o",
        "retries": 1,
        "model_settings": {"temperature": 0.5},
        "system_instructions": [],
        "user_prompt_templates": {"t": ["hello"]},
    }
}


def _make_mock_client_factory() -> LLMClientFactory:
    """创建 mock 的 LLMClientFactory。"""
    mock_factory = MagicMock(spec=LLMClientFactory)
    mock_factory.get_client.return_value = MagicMock()
    return mock_factory


# ── 测试 ──────────────────────────────────────────────────────────────────────
class TestAgentFactory:
    """AgentFactory 的单元测试。"""

    def test_from_config_raises_on_mismatch(self, tmp_path: Path) -> None:
        """YAML Key 与注册表不一致时应抛 ValueError。"""
        bad_config_path = tmp_path / "agents.yaml"
        bad_config_path.write_text(yaml.dump({"unknown_agent": {"model": "gpt-4o"}}), encoding="utf-8")
        providers_path = tmp_path / "providers.yaml"
        providers_path.write_text(
            yaml.dump({"openai": {"type": "openai", "base_url": "...", "api_key_env": "X"}}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="配置一致性校验失败"):
            AgentFactory.from_config(bad_config_path, providers_path)

    def test_create_agent_raises_on_missing_config(self) -> None:
        """agent_key 不存在于配置中时应抛 ValueError。"""
        with patch.dict(SCHEMA_REGISTRY, {"dummy_agent": object()}):
            factory = AgentFactory(_MINIMAL_CONFIG, _make_mock_client_factory())
            with pytest.raises(ValueError, match="未找到配置"):
                factory.create_agent("dummy_agent")

    def test_create_agent_injects_client(self) -> None:
        """验证 CortexAgent 正确接收注入的客户端。"""
        mock_client_factory = _make_mock_client_factory()
        factory = AgentFactory(_MINIMAL_CONFIG, mock_client_factory)
        with patch.dict(SCHEMA_REGISTRY, {"world_builder": object()}):
            agent = factory.create_agent("world_builder")
            mock_client_factory.get_client.assert_called_once_with("openai")
            assert agent.client is mock_client_factory.get_client.return_value

    def test_create_agent_raises_on_missing_provider(self) -> None:
        """agent 配置缺少 provider 字段时应抛 ValueError。"""
        config_no_provider = {
            "world_builder": {
                "model": "gpt-4o",
                "retries": 1,
                "model_settings": {"temperature": 0.5},
                "system_instructions": [],
                "user_prompt_templates": {"t": ["hello"]},
            }
        }
        factory = AgentFactory(config_no_provider, _make_mock_client_factory())
        with patch.dict(SCHEMA_REGISTRY, {"world_builder": object()}):
            with pytest.raises(ValueError, match="缺少 `provider` 字段"):
                factory.create_agent("world_builder")
