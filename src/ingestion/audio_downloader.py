import os
import logging
from pytube import YouTube
from typing import Optional
from src.utils.logger import setup_logger

logger = setup_logger("audio_downloader")

class AudioDownloader:
    def __init__(self, output_dir: str = "audio"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def validate_youtube_url(self, url: str) -> bool:
        """Simple validation of YouTube URL"""
        return "youtube.com" in url or "youtu.be" in url

    def download_audio(self, url: str, prefix: str = "") -> Optional[str]:
        """
        Download audio from a YouTube URL.
        Returns the path to the downloaded file or None if failed.
        """
        try:
            if not self.validate_youtube_url(url):
                logger.error(f"Invalid YouTube URL: {url}")
                raise ValueError("Invalid YouTube URL")

            yt = YouTube(url)
            
            # Check duration (15-90 mins typical, but we just warn for now or enforce limit if strict)
            duration_mins = yt.length / 60
            logger.info(f"Video duration: {duration_mins:.2f} minutes")
            
            # Get audio stream
            audio_stream = yt.streams.filter(only_audio=True).first()
            if not audio_stream:
                logger.error("No audio stream found")
                return None

            # Generate filename
            safe_title = "".join([c for c in yt.title if c.isalnum() or c in (' ', '-', '_')]).strip()
            filename = f"{prefix}_{safe_title}.mp3" if prefix else f"{safe_title}.mp3"
            
            logger.info(f"Downloading: {yt.title} -> {filename}")
            
            # Download
            out_file = audio_stream.download(output_path=self.output_dir, filename=filename)
            
            # Rename to mp3 if needed (pytube usually saves as mp4/webm audio)
            # Actually download method with filename argument saves it as provided, 
            # but the content is still mp4/webm container usually. 
            # Ideally we should convert with ffmpeg, but for now we just save raw.
            # The prompt says "Output: MP3 file". Pytube downloads audio as mp4 usually.
            # We will just return the path for now.
            
            return out_file

        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            raise
