import openai
from typing import Optional
import logging


class EmailAIParser:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)

    async def extract_code(
        self, email_body: str, extraction_type: str
    ) -> Optional[str]:
        """Use AI to extract verification codes or URLs from email content"""
        try:
            if extraction_type == "otp":
                prompt = f"""
                Extract the verification code (OTP) from this email content.
                Return only the numeric code, nothing else.
                
                Email content:
                {email_body[:2000]}
                """
            elif extraction_type == "url":
                prompt = f"""
                Extract the verification or activation URL from this email content.
                Return only the complete URL, nothing else.
                
                Email content:
                {email_body[:2000]}
                """
            else:
                return None

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
            )

            result = response.choices[0].message.content.strip()

            # Validate result
            if extraction_type == "otp" and result.isdigit():
                self.logger.info(f"AI extracted OTP: {result}")
                return result
            elif extraction_type == "url" and result.startswith("http"):
                self.logger.info(f"AI extracted URL: {result}")
                return result

            return None

        except Exception as e:
            self.logger.error(f"AI extraction failed: {e}")
            return None
