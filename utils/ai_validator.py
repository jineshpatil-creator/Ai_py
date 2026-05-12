import os
import pytest
from google import genai
from PIL import Image

class AIValidator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            pytest.skip("GEMINI_API_KEY environment variable not set. Skipping AI visual test. Get your free key at https://aistudio.google.com/app/apikey")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.5-flash'

    def analyze_screenshot(self, screenshot_path: str, prompt: str) -> str:
        """Sends a screenshot and a prompt to Gemini Vision for analysis."""
        img = Image.open(screenshot_path)
        
        from utils.logger import log
        log.info(f"Sending screenshot to Gemini AI for analysis: {screenshot_path}")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt, img]
        )
        return response.text
