import pytest
import os
import json
from unittest.mock import patch, MagicMock
from src.transcription.transcriber import TranscriptionService
import assemblyai as aai

class TestTranscriptionService:
    
    @patch('src.transcription.transcriber.aai.Transcriber')
    @patch.dict(os.environ, {"ASSEMBLYAI_API_KEY": "fake_key"})
    def test_transcribe_audio_success(self, mock_transcriber_cls, tmp_path):
        """Test successful transcription flow with mocked API"""
        
        # Setup mock transcript response
        mock_transcript = MagicMock()
        mock_transcript.status = aai.TranscriptStatus.completed
        mock_transcript.text = "Hello world."
        mock_transcript.id = "fake_id"
        mock_transcript.audio_duration = 10.5
        mock_transcript.confidence = 0.99
        
        # Mock utterances (Should be ignored now)
        # We can remove this setup or keep it to ensure it's not used.
        # But to be clean, let's remove the detailed setup of utterances since we expect them to be ignored.
        mock_transcript.utterances = []
        
        # Setup Transcriber instance mock
        mock_instance = mock_transcriber_cls.return_value
        mock_instance.transcribe.return_value = mock_transcript
        
        # Create dummy audio file
        audio_file = tmp_path / "test_sermon.mp3"
        audio_file.write_text("fake audio content")
        
        # Initialize Service
        service = TranscriptionService()
        
        # Mock output directory to be tmp_path
        # We need to patch where the code writes files.
        # The code writes to "output" directory relative to CWD.
        # We can change CWD or patch open/json.dump, OR just let it write to "output" in current test env 
        # and clean up? 
        # Better: we can rely on the fact that the code uses "output" dir.
        # Let's verify the file existence in "output" folder.
        
        # To avoid cluttering the real "output" folder, we can mock open/json.dump OR 
        # just temporarily patch the output_dir variable in the method? 
        # The method hardcodes "output". 
        # I'll just let it run, it will create files in "output" folder of the project.
        # It's fine for now, or I can clean them up.
        
        result = service.transcribe_audio(str(audio_file))
        
        # Assertions
        assert result['text'] == "Hello world."
        assert "test_sermon_transcript.json" in result['json_path']
        assert os.path.exists(result['json_path'])
        assert os.path.exists(result['raw_path'])
        
        # Verify JSON content
        with open(result['json_path'], 'r') as f:
            data = json.load(f)
            assert data['id'] == "fake_id"
            # Ensure unnecessary fields are removed
            assert 'utterances' not in data
            assert 'confidence' not in data
            assert 'audio_duration' not in data
            assert data['text'] == "Hello world."
            
        # Clean up created files in output folder
        if os.path.exists(result['json_path']):
            os.remove(result['json_path'])
        if os.path.exists(result['raw_path']):
            os.remove(result['raw_path'])

    @patch('src.transcription.transcriber.aai.Transcriber')
    def test_transcribe_audio_file_not_found(self, mock_transcriber_cls):
        service = TranscriptionService()
        with pytest.raises(FileNotFoundError):
            service.transcribe_audio("non_existent.mp3")

    @patch('src.transcription.transcriber.aai.Transcriber')
    @patch.dict(os.environ, {"ASSEMBLYAI_API_KEY": "fake_key"})
    def test_transcribe_audio_api_error(self, mock_transcriber_cls, tmp_path):
        # Setup mock error
        mock_transcript = MagicMock()
        mock_transcript.status = aai.TranscriptStatus.error
        mock_transcript.error = "API Error"
        
        mock_instance = mock_transcriber_cls.return_value
        mock_instance.transcribe.return_value = mock_transcript
        
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("fake")
        
        service = TranscriptionService()
        
        with pytest.raises(Exception, match="Transcription failed: API Error"):
            service.transcribe_audio(str(audio_file))
