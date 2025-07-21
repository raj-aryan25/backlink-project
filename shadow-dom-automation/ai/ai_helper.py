import google.generativeai as genai
from config import GOOGLE_API_KEY


class AIHelper:
    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError(
                "Google AI API key not found. Please set the GOOGLE_API_KEY environment variable."
            )
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    def get_selector_from_html(self, html_content: str, description: str) -> str:
        """
        Uses the Gemini model to find the best CSS selector for an element based on its description.
        """
        # Replace the existing prompt string with this vastly improved version.
        prompt = f"""
You are an expert test automation engineer. Analyze the provided HTML fragment. Your task is to return the single best, most stable CSS selector for the element described by the user.

**Prioritize these attributes in this order:**
1.  `data-testid`, `data-test-id`
2.  `id`
3.  `aria-label`
4.  `role` combined with visible text (e.g., `button:has-text("Submit")`)
5.  A unique combination of `class` names.
6.  The text content itself, if it's unique.

**User's Description:** "{description}"

**HTML to Analyze:**
```html
{html_content}
```
Return only the raw CSS selector and nothing else.
"""
        try:
            response = self.model.generate_content(prompt)
            # Clean up the response to get only the selector
            selector = response.text.strip().replace("`", "").replace("css", "").strip()
            return selector
        except Exception as e:
            print(f"Error communicating with Google AI: {e}")
            return None
