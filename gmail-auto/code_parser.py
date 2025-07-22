import base64
import re
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class CodeParser:
    """Parses email content to extract specific information, like a verification code."""

    def __init__(self, code_parser_config, ai_parser_config):
        """Initializes the parser with extraction configuration."""
        self.regex = code_parser_config.get("regex", "")
        self.ai_config = ai_parser_config

        if self.ai_config.get("enabled"):
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
            else:
                print(
                    "Warning: AI parsing is enabled, but GOOGLE_API_KEY environment variable is not set."
                )
                # Disable AI if key is not found
                self.ai_config["enabled"] = False

    def get_body(self, payload):
        """
        Extracts the most suitable text body from the email payload.
        Prefers 'text/plain', but falls back to 'text/html'.
        """
        if "parts" in payload:
            for part in payload.get("parts", []):
                # Recurse for nested parts
                if "parts" in part:
                    body, mime_type = self.get_body(part)
                    if body:
                        return body, mime_type

                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data")
                    if data:
                        return (
                            base64.urlsafe_b64decode(data.encode("UTF-8")).decode(
                                "utf-8"
                            ),
                            "text/plain",
                        )

        # If no plain text part is found, look for HTML
        if "parts" in payload:
            for part in payload.get("parts", []):
                if part.get("mimeType") == "text/html":
                    data = part.get("body", {}).get("data")
                    if data:
                        return (
                            base64.urlsafe_b64decode(data.encode("UTF-8")).decode(
                                "utf-8"
                            ),
                            "text/html",
                        )

        # Fallback for non-multipart messages
        if "body" in payload:
            data = payload.get("body", {}).get("data")
            if data:
                mime_type = payload.get("mimeType", "text/plain")
                body = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("utf-8")
                return body, mime_type

        return None, None

    def extract_code(self, body, mime_type):
        """
        Extracts a code from the email body using AI or regex.
        """
        text_to_search = body
        if mime_type == "text/html":
            # Simple regex to strip HTML tags and decode entities
            text_to_search = re.sub(r"<[^>]+>", " ", body)
            text_to_search = re.sub(
                r"=\s*", "", text_to_search
            )  # Remove quoted-printable soft line breaks

        # Try AI extraction first if enabled
        if self.ai_config.get("enabled"):
            print("Attempting extraction with AI...")
            try:
                model = genai.GenerativeModel("gemini-pro")
                prompt = self.ai_config.get("prompt", "") + text_to_search
                response = model.generate_content(prompt)
                extracted_code = response.text.strip()
                # Basic validation to ensure the AI returned something that looks like a code
                if extracted_code and extracted_code.isdigit():
                    print("Successfully extracted code with AI.")
                    return extracted_code
                else:
                    print("AI did not return a valid code. Falling back to regex.")
            except Exception as e:
                print(
                    f"An error occurred during AI extraction: {e}. Falling back to regex."
                )

        # Fallback to regex
        print("Attempting extraction with regex...")
        if not self.regex:
            print("No extraction regex defined in config.")
            return None

        match = re.search(self.regex, text_to_search, re.DOTALL)

        if match:
            # Return the first captured group
            return match.group(1)
        else:
            print("Could not find a match for the extraction regex.")
            return None
