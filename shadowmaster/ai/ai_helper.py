# ai/ai_helper.py

import google.generativeai as genai
from config import GOOGLE_API_KEY
import logging


class AIHelper:
    """
    Handles all communication with the Google Generative AI model
    to dynamically find element selectors.
    """

    def __init__(self):
        """
        Initializes the AI Helper and configures the Google AI SDK.
        """
        if not GOOGLE_API_KEY:
            raise ValueError(
                "Google AI API key not found. Please set the GOOGLE_API_KEY environment variable."
            )
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    def get_selector_from_html(self, html_content: str, description: str) -> str | None:
        """
        Uses the Gemini model to find the best CSS selector for an element
        based on its description and the page's HTML.

        Args:
            html_content: The full HTML content of the page.
            description: A natural language description of the target element.

        Returns:
            The most robust CSS selector as a string, or None if an error occurs.
        """
        prompt = f"""
        Analyze the following HTML code. Your task is to act as an expert test automation engineer.
        Based on the user's description, provide the single most robust and precise CSS selector to locate the element.
        The selector must be able to pierce through any open Shadow DOMs.
        Prioritize selectors based on unique attributes like 'id', 'data-testid', 'role', 'name', or 'aria-label'. Avoid brittle selectors.

        HTML Content:
        ```html
        {html_content}
        ```

        User's Description of the element to find:
        "{description}"

        Provide only the CSS selector as a single line of text and nothing else.
        For example: `button[aria-label="Accept all cookies"]`
        """
        try:
            response = self.model.generate_content(prompt)
            # Clean up the response to ensure only the selector is returned.
            selector = response.text.strip().replace("`", "").replace("css", "").strip()
            logging.info(f"AI suggested selector: '{selector}'")
            return selector
        except Exception as e:
            logging.error(f"Error communicating with Google AI: {e}")
            return None
