import pytest
from unittest.mock import patch, MagicMock
from src.utils.bible_fetcher import BibleFetcher

@pytest.fixture
def bible_fetcher():
    return BibleFetcher()

def test_get_scripture_success(bible_fetcher):
    """Test successful scripture retrieval"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "reference": "John 3:16",
        "text": "For God so loved the world..."
    }

    with patch('requests.get', return_value=mock_response) as mock_get:
        text = bible_fetcher.get_scripture("John 3:16", "kjv")
        
        assert text == "For God so loved the world..."
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "John 3:16" in args[0]
        assert kwargs['params']['translation'] == 'kjv'

def test_get_scripture_not_found(bible_fetcher):
    """Test handling of 404 or other errors"""
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch('requests.get', return_value=mock_response):
        text = bible_fetcher.get_scripture("Invalid 99:99")
        assert text is None

def test_get_scripture_exception(bible_fetcher):
    """Test handling of connection exceptions"""
    with patch('requests.get', side_effect=Exception("Connection error")):
        text = bible_fetcher.get_scripture("John 3:16")
        assert text is None
