import pytest
import os
from unittest.mock import patch, MagicMock
from src.providers.llm_factory import get_llm_client

class TestLLMFactory:
    
    @patch('src.providers.llm_factory.os.getenv')
    def test_get_llm_client_gemini(self, mock_getenv):
        """Test Gemini client creation"""
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'gemini',
            'LLM_API_KEY': 'fake_key',
            'LLM_MODEL': 'gemini-pro'
        }.get(key, default)

        with patch('google.generativeai.configure') as mock_configure, \
             patch('google.generativeai.GenerativeModel') as mock_model:
            
            client, provider = get_llm_client()
            
            assert provider == 'gemini'
            mock_configure.assert_called_with(api_key='fake_key')
            mock_model.assert_called_with('gemini-pro')

    @patch('src.providers.llm_factory.os.getenv')
    def test_get_llm_client_openai(self, mock_getenv):
        """Test OpenAI client creation"""
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'openai',
            'LLM_API_KEY': 'fake_key',
            'LLM_MODEL': 'gpt-4'
        }.get(key, default)

        with patch('openai.OpenAI') as mock_openai:
            client, provider = get_llm_client()
            
            assert provider == 'openai'
            mock_openai.assert_called_with(api_key='fake_key')

    @patch('src.providers.llm_factory.os.getenv')
    def test_get_llm_client_openrouter(self, mock_getenv):
        """Test OpenRouter client creation"""
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'openrouter',
            'LLM_API_KEY': 'fake_key',
            'LLM_MODEL': 'model'
        }.get(key, default)

        with patch('openai.OpenAI') as mock_openai:
            client, provider = get_llm_client()
            
            assert provider == 'openrouter'
            mock_openai.assert_called_with(
                base_url="https://openrouter.ai/api/v1",
                api_key='fake_key'
            )

    @patch('src.providers.llm_factory.os.getenv')
    def test_get_llm_client_unsupported(self, mock_getenv):
        """Test unsupported provider"""
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'unknown',
            'LLM_API_KEY': 'fake_key'
        }.get(key, default)

        with pytest.raises(ValueError, match="Unsupported provider: unknown"):
            get_llm_client()
