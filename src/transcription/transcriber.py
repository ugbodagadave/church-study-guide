import assemblyai as aai
import os
import json
from typing import Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger("transcription_service")

class TranscriptionService:
    def __init__(self):
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            logger.warning("ASSEMBLYAI_API_KEY not found in environment variables.")
        else:
            aai.settings.api_key = api_key
        
        self.transcriber = aai.Transcriber()

    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribes audio file using AssemblyAI.
        Returns a dictionary containing:
        - text: Raw text
        - json_path: Path to saved JSON structure
        - raw_path: Path to saved raw text
        - structured_data: The full structured data dict
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Starting transcription for: {audio_path}")

        # Configuration matching requirements
        # Note: speech_model=aai.SpeechModel.best maps to Universal-1
        config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best, 
            speaker_labels=False,  # Disabled per user request
            language_detection=True,
            punctuate=True,
            format_text=True
        )

        try:
            transcript = self.transcriber.transcribe(audio_path, config=config)
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")

            # Prepare outputs
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save Raw Text
            raw_text_path = os.path.join(output_dir, f"{base_name}_transcript.txt")
            with open(raw_text_path, "w", encoding="utf-8") as f:
                f.write(transcript.text)
                
            # Prepare Structured JSON (Simplified per user request)
            structured_data = {
                "id": transcript.id,
                "status": transcript.status,
                "text": transcript.text
            }
            
            # Save JSON
            json_path = os.path.join(output_dir, f"{base_name}_transcript.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(structured_data, f, indent=2)

            logger.info(f"Transcription completed. Saved to {raw_text_path} and {json_path}")
            
            return {
                "text": transcript.text,
                "json_path": json_path,
                "raw_path": raw_text_path,
                "structured_data": structured_data
            }

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
