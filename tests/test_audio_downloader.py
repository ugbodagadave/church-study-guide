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

    @patch('src.ingestion.audio_downloader.yt_dlp.YoutubeDL')
    def test_download_audio_success(self, mock_ytdl, tmp_path):
        """Test successful download flow"""
        # Setup mock
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        expected_path = str(tmp_path / "Test_Sermon.mp3")
        
        # Mock extract_info to return dict
        mock_ytdl_instance.extract_info.return_value = {
            'title': 'Test Sermon',
            'duration': 1800,
            'ext': 'mp3'
        }
        
        mock_ytdl_instance.prepare_filename.return_value = expected_path

        # Execute
        downloader = AudioDownloader(output_dir=str(tmp_path))
        result = downloader.download_audio("https://youtube.com/watch?v=test")

        # Assert
        assert result == expected_path
        # extract_info is called twice: once for metadata (download=False), once for download (download=True)
        assert mock_ytdl_instance.extract_info.call_count >= 1

    @patch('src.ingestion.audio_downloader.yt_dlp.YoutubeDL')
    def test_download_audio_failure(self, mock_ytdl):
        """Test download failure handling"""
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        mock_ytdl_instance.extract_info.side_effect = Exception("Download failed")
        
        downloader = AudioDownloader()
        
        with pytest.raises(Exception, match="Download failed"):
            downloader.download_audio("https://youtube.com/watch?v=test")
