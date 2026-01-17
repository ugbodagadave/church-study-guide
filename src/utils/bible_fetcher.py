import requests
from typing import Optional, Dict, Any
from src.utils.logger import setup_logger

logger = setup_logger("bible_fetcher")

class BibleFetcher:
    BASE_URL = "https://bible-api.com/"

    def get_scripture(self, reference: str, version: str = "kjv") -> Optional[str]:
        """
        Fetches the text of a scripture reference from bible-api.com.
        
        Args:
            reference: The bible reference (e.g., "John 3:16")
            version: The bible version (default: "kjv"). 
                     Supported: kjv, web, webbe, oeb-us, oeb-cw, web, webbe, clementina, almeida, rvr
        
        Returns:
            The verse text as a string, or None if failed.
        """
        if not reference:
            return None

        # Clean reference (remove quotes, extra spaces)
        clean_ref = reference.strip().replace('"', '').replace("'", "")
        
        # Handle multiple references separated by semi-colons
        if ';' in clean_ref:
            refs = [r.strip() for r in clean_ref.split(';')]
            full_text = []
            for ref in refs:
                text = self._fetch_single_ref(ref, version)
                if text:
                    full_text.append(text)
            return " ".join(full_text) if full_text else None

        return self._fetch_single_ref(clean_ref, version)

    def _fetch_single_ref(self, reference: str, version: str) -> Optional[str]:
        # Construct URL
        # API format: https://bible-api.com/John 3:16?translation=kjv
        url = f"{self.BASE_URL}{reference}"
        params = {"translation": version}

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # The API returns 'text' which combines all verses. Remove newlines for flow.
                return data.get("text", "").replace('\n', ' ').strip()
            else:
                logger.warning(f"Failed to fetch scripture {reference}: Status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching scripture {reference}: {e}")
            return None
