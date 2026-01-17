import os
import yt_dlp
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
        Download audio from a YouTube URL using yt-dlp.
        Returns the path to the downloaded file or None if failed.
        """
        try:
            if not self.validate_youtube_url(url):
                logger.error(f"Invalid YouTube URL: {url}")
                raise ValueError("Invalid YouTube URL")

            # Get metadata first
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                try:
                    info_dict = ydl.extract_info(url, download=False)
                    video_title = info_dict.get('title', 'audio')
                    duration = info_dict.get('duration', 0)
                    logger.info(f"Video duration: {duration/60:.2f} minutes")
                except Exception as e:
                    logger.error(f"Failed to extract info: {e}")
                    raise

            # Sanitized title
            safe_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '-', '_')]).strip()
            
            # Configure download options
            # Since ffmpeg is missing, we just download the best audio format
            out_tmpl = os.path.join(self.output_dir, f"{prefix}_{safe_title}.%(ext)s" if prefix else f"{safe_title}.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': out_tmpl,
                'quiet': True,
                'no_warnings': True,
            }
            
            logger.info(f"Downloading: {video_title}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # ydl.prepare_filename(info) gives the expected filename with the correct extension
                filename = ydl.prepare_filename(info)
                
            logger.info(f"Downloaded to: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            raise
