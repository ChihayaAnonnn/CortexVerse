"""OpenAICompatibleClient 测试。"""

from unittest.mock import MagicMock, patch

import pytest

from cortexverse.infrastructure.llm_clients.openai_client import OpenAICompatibleClient


class TestOpenAICompatibleClient:
    """OpenAICompatibleClient 的单元测试。"""

    def test_create_client_raises_on_missing_env(self) -> None:
        """验证环境变量缺失时抛出 EnvironmentError。"""
        client = OpenAICompatibleClient(
            base_url="https://api.test.com/v1",
            api_key_env="MISSING_API_KEY",
            provider_name="test",
        )
        with pytest.raises(EnvironmentError, match="MISSING_API_KEY"):
            client.create_client()

    @patch("cortexverse.infrastructure.llm_clients.openai_client.instructor.from_openai")
    @patch("cortexverse.infrastructure.llm_clients.openai_client.openai.AsyncOpenAI")
    @patch.dict("os.environ", {"TEST_API_KEY": "sk-test-key"})
    def test_create_client_passes_base_url(self, mock_openai_cls: MagicMock, mock_from_openai: MagicMock) -> None:
        """验证 base_url 和 api_key 正确传递给 AsyncOpenAI。"""
        mock_openai_cls.return_value = MagicMock()

        client = OpenAICompatibleClient(
            base_url="https://api.deepseek.com",
            api_key_env="TEST_API_KEY",
            provider_name="deepseek",
        )
        client.create_client()

        mock_openai_cls.assert_called_once_with(
            api_key="sk-test-key",
            base_url="https://api.deepseek.com",
        )

    @patch("cortexverse.infrastructure.llm_clients.openai_client.openai.AsyncOpenAI")
    @patch("cortexverse.infrastructure.llm_clients.openai_client.instructor.from_openai")
    @patch.dict("os.environ", {"TEST_API_KEY": "sk-test-key"})
    def test_create_client_returns_instructor(self, mock_from_openai: MagicMock, mock_openai_cls: MagicMock) -> None:
        """验证返回 instructor 包装后的客户端。"""
        mock_native = MagicMock()
        mock_openai_cls.return_value = mock_native
        mock_instructor = MagicMock()
        mock_from_openai.return_value = mock_instructor

        client = OpenAICompatibleClient(
            base_url="https://api.test.com/v1",
            api_key_env="TEST_API_KEY",
        )
        result = client.create_client()

        mock_from_openai.assert_called_once_with(mock_native)
        assert result is mock_instructor

    def test_provider_name(self) -> None:
        """验证 provider_name 属性。"""
        client = OpenAICompatibleClient(
            base_url="https://api.test.com/v1",
            api_key_env="TEST_API_KEY",
            provider_name="deepseek",
        )
        assert client.provider_name == "deepseek"
