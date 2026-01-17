import argparse
import os
import sys
import json
from dotenv import load_dotenv

# Ensure project root is in sys.path so 'src' imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.audio_downloader import AudioDownloader
from src.transcription.transcriber import TranscriptionService
from src.generation.content_generator import ContentGenerator
from src.design.pdf_designer import PDFDesigner
from src.utils.logger import setup_logger

logger = setup_logger("main")

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Church Study Guide Generator")
    parser.add_argument("--url", help="YouTube URL to download")
    parser.add_argument("--file", help="Local audio file path")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "openai", "groq"], help="LLM Provider")
    parser.add_argument("--logo", help="Path to church logo for PDF branding")
    parser.add_argument("--series", default="Sermon Series", help="Series Title")
    parser.add_argument("--preacher", default="", help="Name of the Preacher")
    parser.add_argument("--bible-version", default="kjv", choices=["kjv", "web", "rvr"], help="Bible Version (default: kjv)")
    
    args = parser.parse_args()
    
    # 1. Audio Ingestion
    audio_path = args.file
    if args.url:
        # Sanitize URL (remove quotes/backticks if user accidentally included them)
        clean_url = args.url.strip("`'\" ")
        logger.info(f"Downloading audio from {clean_url}...")
        downloader = AudioDownloader()
        try:
            audio_path = downloader.download_audio(clean_url)
        except Exception as e:
            logger.error(f"Download failed: {e}")
            sys.exit(1)
            
    if not audio_path or not os.path.exists(audio_path):
        logger.error("No valid audio file provided or found.")
        sys.exit(1)
        
    # 2. Transcription
    logger.info("Transcribing audio...")
    transcriber = TranscriptionService()
    try:
        transcript_data = transcriber.transcribe_audio(audio_path)
        transcript_text = transcript_data.get("text", "")
        if not transcript_text:
            raise ValueError("Empty transcript generated.")
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        sys.exit(1)
        
    # 3. Content Generation
    logger.info(f"Generating devotional content using {args.provider}...")
    generator = ContentGenerator()
    # Force provider if needed, though ContentGenerator uses factory internally based on env or args.
    # Current ContentGenerator implementation loads from factory but doesn't take provider arg in init.
    # We might want to pass it or rely on env. For now, assuming factory handles it or we update ContentGenerator.
    # *Correction*: ContentGenerator uses `get_llm_client` which checks env. 
    # To support CLI arg override, we'd need to modify ContentGenerator or set env var.
    # Let's set the env var for the session to ensure factory picks it up.
    os.environ["LLM_PROVIDER"] = args.provider
    
    try:
        content_json = generator.generate_content(transcript_text, bible_version=args.bible_version)
        # Override series title if provided in CLI and not just default
        if args.series != "Sermon Series" or "series_title" not in content_json:
            content_json["series_title"] = args.series
        # Add preacher name to content json
        content_json["preacher_name"] = args.preacher
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        sys.exit(1)
        
    # 4. PDF Design
    logger.info("Generating PDF...")
    designer = PDFDesigner()
    output_pdf = f"output/{content_json.get('series_title', 'study_guide').replace(' ', '_')}.pdf"
    
    try:
        designer.create_pdf(content_json, output_pdf, args.logo)
        logger.info(f"Process Complete! Study Guide available at: {output_pdf}")
        print(f"\nSUCCESS: Study Guide generated at {output_pdf}")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
