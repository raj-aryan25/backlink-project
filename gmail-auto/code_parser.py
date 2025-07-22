import base64
import re


class CodeParser:
    """Parses email content to extract specific information, like a verification code."""

    def __init__(self, config):
        """Initializes the parser with extraction configuration."""
        self.regex = config.get("regex", "")

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
        Uses regex to extract a code from the email body.
        Strips HTML tags if necessary.
        """
        if not self.regex:
            print("No extraction regex defined in config.")
            return None

        text_to_search = body
        if mime_type == "text/html":
            # Simple regex to strip HTML tags and decode entities
            text_to_search = re.sub(r"<[^>]+>", " ", body)
            text_to_search = re.sub(
                r"=\s*", "", text_to_search
            )  # Remove quoted-printable soft line breaks

        match = re.search(self.regex, text_to_search, re.DOTALL)

        if match:
            # Return the first captured group
            return match.group(1)
        else:
            print("Could not find a match for the extraction regex.")
            return None
