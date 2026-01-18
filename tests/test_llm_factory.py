import pytest
import types
from unittest.mock import patch, MagicMock
from src.providers.llm_factory import get_llm_client


class TestLLMFactory:
    @patch('src.providers.llm_factory.os.getenv')
    def test_get_llm_client_gemini(self, mock_getenv):
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'gemini',
            'LLM_API_KEY': 'fake_key',
        }.get(key, default)

        dummy_client_cls = MagicMock()
        google_module = types.ModuleType('google')
        google_module.genai = types.SimpleNamespace(Client=dummy_client_cls)

        with patch.dict('sys.modules', {'google': google_module}):
            client, provider = get_llm_client()

        assert provider == 'gemini'
        dummy_client_cls.assert_called_with(api_key='fake_key')
        assert client is dummy_client_cls.return_value

    @patch('src.providers.llm_factory.os.getenv')
    def test_get_llm_client_openai(self, mock_getenv):
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'openai',
            'LLM_API_KEY': 'fake_key',
        }.get(key, default)

        openai_module = types.ModuleType('openai')
        openai_client_cls = MagicMock()
        openai_module.OpenAI = openai_client_cls

        with patch.dict('sys.modules', {'openai': openai_module}):
            client, provider = get_llm_client()

        assert provider == 'openai'
        openai_client_cls.assert_called_with(api_key='fake_key')
        assert client is openai_client_cls.return_value

    @patch('src.providers.llm_factory.os.getenv')
    def test_get_llm_client_openrouter(self, mock_getenv):
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'openrouter',
            'LLM_API_KEY': 'fake_key',
        }.get(key, default)

        openai_module = types.ModuleType('openai')
        openai_client_cls = MagicMock()
        openai_module.OpenAI = openai_client_cls

        with patch.dict('sys.modules', {'openai': openai_module}):
            client, provider = get_llm_client()

        assert provider == 'openrouter'
        openai_client_cls.assert_called_with(
            base_url="https://openrouter.ai/api/v1",
            api_key='fake_key',
        )
        assert client is openai_client_cls.return_value

    @patch('src.providers.llm_factory.os.getenv')
    def test_get_llm_client_unsupported(self, mock_getenv):
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'unknown',
            'LLM_API_KEY': 'fake_key',
        }.get(key, default)

        with pytest.raises(ValueError, match="Unsupported provider: unknown"):
            get_llm_client()
