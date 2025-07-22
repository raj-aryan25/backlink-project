import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class GeminiWrapper:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def analyze_screenshot(self, screenshot_bytes, prompt):
        response = await self.model.generate_content_async(
            [prompt, {"mime_type": "image/png", "data": screenshot_bytes}]
        )
        return response

    async def get_button_text(self, response):
        if not response or not response.text:
            raise ValueError("Response from Gemini is empty or invalid.")
        button_text = response.text.strip().replace("'", "").replace('"', "")
        if not button_text:
            raise ValueError("Gemini could not identify a button text.")
        return button_text

    async def get_login_placeholders(self, response):
        if not response or not response.text:
            raise ValueError("Response from Gemini is empty or invalid.")
        credential_boxes = eval(response.text.strip())
        if not credential_boxes or not isinstance(credential_boxes, dict):
            raise ValueError("Gemini did not return valid credential boxes.")
        email_placeholder = credential_boxes.get("email", "")
        password_placeholder = credential_boxes.get("password", "")
        return email_placeholder, password_placeholder
