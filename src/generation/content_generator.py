import json
import re
import os
from typing import Dict, Any, Optional
from src.providers.llm_factory import get_llm_client
from src.generation.prompts import DEVOTIONAL_SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.utils.logger import setup_logger
from src.utils.bible_fetcher import BibleFetcher

logger = setup_logger("content_generator")

class ContentGenerator:
    def __init__(self):
        self.client, self.provider = get_llm_client()
        self.bible_fetcher = BibleFetcher()
        logger.info(f"Initialized ContentGenerator with provider: {self.provider}")

    def generate_content(self, transcript_text: str, bible_version: str = "kjv") -> Dict[str, Any]:
        """
        Generates devotional content from transcript text.
        """
        if not transcript_text:
            raise ValueError("Transcript text cannot be empty")

        prompt = USER_PROMPT_TEMPLATE.format(transcript=transcript_text)
        
        try:
            response_text = self._call_llm(prompt)
            parsed_json = self._parse_json_response(response_text)
            self._validate_schema(parsed_json)
            
            # Enrich with actual scripture text
            self._enrich_scriptures(parsed_json, bible_version)
            
            # Save output
            self._save_output(parsed_json)
            
            return parsed_json
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise

    def _enrich_scriptures(self, data: Dict[str, Any], version: str):
        """Fetches scripture text for each day and memory verse using BibleFetcher"""
        logger.info(f"Fetching scripture texts (Version: {version.upper()})...")
        
        # Enrich Memory Verse
        mv_ref = data.get("memory_verse_reference")
        if mv_ref:
            text = self.bible_fetcher.get_scripture(mv_ref, version)
            if text:
                data["memory_verse"] = f"{mv_ref} ({version.upper()}):\n{text}"
            else:
                data["memory_verse"] = f"{mv_ref} (Text not found)"
        else:
            # Backward compatibility if LLM outputs old key or fails
            if "memory_verse" not in data:
                 data["memory_verse"] = "Memory verse not available"

        # Enrich Daily Scriptures
        for day in data.get("days", []):
            ref = day.get("scripture_reference")
            # If scripture_reference is missing, check if 'scripture' exists and use it as reference
            if not ref and "scripture" in day:
                 ref = day["scripture"]
                 
            if ref:
                text = self.bible_fetcher.get_scripture(ref, version)
                if text:
                    day["scripture"] = f"{ref} ({version.upper()}): \"{text}\""
                else:
                    # Fallback: keep existing or mark as unavailable
                    if "scripture" not in day or not day["scripture"]:
                         day["scripture"] = f"{ref} (Text not found)"
            else:
                logger.warning(f"No scripture reference found for Day {day.get('day')}")

    def _call_llm(self, user_prompt: str) -> str:
        """Dispatches call to specific LLM provider"""
        logger.info(f"Sending request to {self.provider}...")
        
        if self.provider == 'gemini':
            # Google Generative AI
            # System instructions are set at model creation or part of the prompt in some versions.
            # For gemini-pro, we can prepend system prompt or use system_instruction if supported by lib version.
            # Simpler to just prepend for broad compatibility if system_instruction param isn't strictly enforced.
            # However, google-generativeai v0.3+ supports system_instruction.
            # Let's try to use the chat interface or generate_content with system prompt in context.
            
            full_prompt = f"{DEVOTIONAL_SYSTEM_PROMPT}\n\n{user_prompt}"
            response = self.client.generate_content(full_prompt)
            return response.text

        elif self.provider in ['openai', 'openrouter', 'groq']:
            # OpenAI-compatible APIs
            response = self.client.chat.completions.create(
                model=os.getenv('LLM_MODEL'),
                messages=[
                    {"role": "system", "content": DEVOTIONAL_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"} if self.provider == 'openai' else None 
                # Groq/OpenRouter might not support response_format="json_object" identically in all models, 
                # but we instruct JSON in prompt.
            )
            return response.choices[0].message.content
            
        else:
            raise ValueError(f"Provider {self.provider} not implemented in generation logic")

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Extracts and parses JSON from response text"""
        # Remove markdown code blocks if present
        cleaned_text = re.sub(r'```json\s*|\s*```', '', response_text).strip()
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response. Raw text logged.")
            logger.debug(cleaned_text)
            raise ValueError("LLM did not return valid JSON")

    def _validate_schema(self, data: Dict[str, Any]):
        """Simple schema validation"""
        # Note: 'memory_verse' changed to 'memory_verse_reference' in new schema
        required_keys = ["series_title", "days", "key_quotes"] 
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key in JSON: {key}")
        
        # Check for memory verse reference or legacy memory verse
        if "memory_verse_reference" not in data and "memory_verse" not in data:
             raise ValueError("Missing memory_verse_reference in JSON")
        
        if not isinstance(data["days"], list):
            raise ValueError("'days' must be a list")
            
        # Requirement: 6 days (or 5 days + cover, but prompt asks for 6 days)
        # Prompt says: "Create a structured 6-day guide"
        if len(data["days"]) < 5: 
             # Allow 5 or 6, just warn if low.
             logger.warning(f"Generated {len(data['days'])} days. Expected 6.")

    def _save_output(self, data: Dict[str, Any]):
        """Saves generated content to output directory"""
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Use series title or generic name for filename
        safe_title = "".join([c for c in data.get("series_title", "devotional") if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{safe_title.replace(' ', '_')}_content.json"
        path = os.path.join(output_dir, filename)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved generated content to {path}")
