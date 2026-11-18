import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Unified LLM interface supporting Google Gemini via the official google-genai SDK,
    with structured JSON response enforcement and graceful fallback.
    """
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
        self.default_model = getattr(settings, 'AI_DEFAULT_MODEL', 'gemini-2.5-flash')
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize google-genai Client: {e}")

    def generate_json(self, prompt: str, system_instruction: str = "") -> dict:
        """
        Sends prompt to Gemini model and parses the returned structured JSON output.
        """
        if not self.client or not self.api_key:
            logger.info("No Gemini API key configured. Utilizing heuristic deterministic fallback.")
            return {}

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                system_instruction=system_instruction or "You are an expert cybersecurity analysis engine. Output valid JSON only.",
                response_mime_type="application/json",
                temperature=0.1,  # Low temperature for precise security reasoning
            )

            response = self.client.models.generate_content(
                model=self.default_model,
                contents=prompt,
                config=config
            )

            text = response.text.strip()
            return json.loads(text)

        except Exception as e:
            logger.error(f"LLM API generation error: {e}")
            return {}
