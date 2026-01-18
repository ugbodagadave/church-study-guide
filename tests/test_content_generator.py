import pytest
from unittest.mock import patch, MagicMock
from src.generation.content_generator import ContentGenerator

class TestContentGenerator:
    
    @patch('src.generation.content_generator.get_llm_client')
    def test_init(self, mock_get_client):
        mock_get_client.return_value = (MagicMock(), 'gemini')
        generator = ContentGenerator()
        assert generator.provider == 'gemini'

    @patch('src.generation.content_generator.BibleFetcher')
    @patch('src.generation.content_generator.get_llm_client')
    def test_generate_content_gemini_success(self, mock_get_client, mock_bible_fetcher):
        # Setup Gemini mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        # Mock with valid days containing 'question'
        day_mock = '{"question": "Q1", "title": "T", "scripture_reference": "Ref", "reflection": "R", "prayer": "P"}'
        days_json = f'[{day_mock}, {day_mock}, {day_mock}, {day_mock}, {day_mock}, {day_mock}]'
        mock_response.text = f'{{"series_title": "Test Series", "memory_verse_reference": "John 3:16", "days": {days_json}, "key_quotes": []}}'
        mock_client.generate_content.return_value = mock_response
        
        mock_get_client.return_value = (mock_client, 'gemini')
        
        # Setup BibleFetcher mock
        mock_fetcher_instance = mock_bible_fetcher.return_value
        mock_fetcher_instance.get_scripture.return_value = "For God so loved..."

        generator = ContentGenerator()
        result = generator.generate_content("transcript text")
        
        assert result['series_title'] == "Test Series"
        assert len(result['days']) == 6
        assert "John 3:16" in result['memory_verse']
        mock_client.generate_content.assert_called_once()

    @patch('src.generation.content_generator.BibleFetcher')
    @patch('src.generation.content_generator.get_llm_client')
    @patch('src.generation.content_generator.os.getenv')
    def test_generate_content_openai_success(self, mock_getenv, mock_get_client, mock_bible_fetcher):
        # Setup OpenAI mock
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_message = MagicMock()
        # Mock with valid days containing 'question'
        day_mock = '{"question": "Q1", "title": "T", "scripture_reference": "Ref", "reflection": "R", "prayer": "P"}'
        days_json = f'[{day_mock}, {day_mock}, {day_mock}, {day_mock}, {day_mock}, {day_mock}]'
        mock_message.content = f'{{"series_title": "Test Series", "memory_verse_reference": "John 3:16", "days": {days_json}, "key_quotes": []}}'
        mock_completion.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_completion
        
        mock_get_client.return_value = (mock_client, 'openai')
        mock_getenv.return_value = 'gpt-4'
        
        # Setup BibleFetcher mock
        mock_fetcher_instance = mock_bible_fetcher.return_value
        mock_fetcher_instance.get_scripture.return_value = "For God so loved..."

        generator = ContentGenerator()
        result = generator.generate_content("transcript text")
        
        assert result['series_title'] == "Test Series"
        mock_client.chat.completions.create.assert_called_once()

    @patch('src.generation.content_generator.get_llm_client')
    def test_validate_schema_failure(self, mock_get_client):
        mock_client = MagicMock()
        # Missing required keys
        mock_response = MagicMock()
        mock_response.text = '{"days": []}' 
        mock_client.generate_content.return_value = mock_response
        
        mock_get_client.return_value = (mock_client, 'gemini')
        
        generator = ContentGenerator()
        
        with pytest.raises(ValueError, match="Missing required key"):
            generator.generate_content("transcript")

    @patch('src.generation.content_generator.get_llm_client')
    def test_json_parse_failure(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'Not JSON'
        mock_client.generate_content.return_value = mock_response
        
        mock_get_client.return_value = (mock_client, 'gemini')
        
        generator = ContentGenerator()
        
        with pytest.raises(ValueError, match="LLM did not return valid JSON"):
            generator.generate_content("transcript")
