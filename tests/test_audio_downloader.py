import pytest
from unittest.mock import patch, MagicMock
from src.ingestion.audio_downloader import AudioDownloader
import os

class TestAudioDownloader:
    
    def test_init_creates_dir(self, tmp_path):
        """Test that init creates the output directory"""
        output_dir = tmp_path / "audio_test"
        downloader = AudioDownloader(output_dir=str(output_dir))
        assert os.path.exists(output_dir)

    def test_validate_youtube_url(self):
        downloader = AudioDownloader()
        assert downloader.validate_youtube_url("https://www.youtube.com/watch?v=123")
        assert downloader.validate_youtube_url("https://youtu.be/123")
        assert not downloader.validate_youtube_url("https://facebook.com/video")

    @patch('src.ingestion.audio_downloader.YouTube')
    def test_download_audio_success(self, mock_youtube, tmp_path):
        """Test successful download flow"""
        # Setup mock
        mock_yt_instance = MagicMock()
        mock_youtube.return_value = mock_yt_instance
        
        mock_yt_instance.length = 1800 # 30 mins
        mock_yt_instance.title = "Test Sermon"
        
        mock_stream = MagicMock()
        mock_yt_instance.streams.filter.return_value.first.return_value = mock_stream
        
        expected_path = str(tmp_path / "Test_Sermon.mp3")
        mock_stream.download.return_value = expected_path

        # Execute
        downloader = AudioDownloader(output_dir=str(tmp_path))
        result = downloader.download_audio("https://youtube.com/watch?v=test")

        # Assert
        assert result == expected_path
        mock_stream.download.assert_called_once()
        args, kwargs = mock_stream.download.call_args
        assert kwargs['filename'] == "Test Sermon.mp3"

    @patch('src.ingestion.audio_downloader.YouTube')
    def test_download_audio_failure(self, mock_youtube):
        """Test download failure handling"""
        mock_youtube.side_effect = Exception("Download failed")
        
        downloader = AudioDownloader()
        
        with pytest.raises(Exception, match="Download failed"):
            downloader.download_audio("https://youtube.com/watch?v=test")
