import re
from typing import Optional, List, Dict
import logging
from bs4 import BeautifulSoup


class CodeParser:
    def __init__(self, patterns: Dict[str, List[str]]):
        self.patterns = patterns
        self.logger = logging.getLogger(__name__)

    def extract_otp(self, text: str) -> Optional[str]:
        """Extract OTP code from text"""
        return self._extract_by_type(text, "otp")

    def extract_url(self, text: str) -> Optional[str]:
        """Extract verification URL from text"""
        return self._extract_by_type(text, "url")

    def _extract_by_type(self, text: str, extraction_type: str) -> Optional[str]:
        """Extract code/URL based on type"""
        patterns = self.patterns.get(extraction_type, [])

        # Clean HTML if present
        if "<html" in text.lower() or "<body" in text.lower():
            soup = BeautifulSoup(text, "html.parser")
            text = soup.get_text()

        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1) if match.groups() else match.group(0)
                    self.logger.info(f"Extracted {extraction_type}: {result}")
                    return result
            except Exception as e:
                self.logger.error(f"Regex error with pattern {pattern}: {e}")
                continue

        return None

    def extract_codes_from_email(
        self, email_body: str, extraction_type: str
    ) -> List[str]:
        """Extract all codes/URLs from email body"""
        patterns = self.patterns.get(extraction_type, [])
        results = []

        # Clean HTML if present
        if "<html" in email_body.lower() or "<body" in email_body.lower():
            soup = BeautifulSoup(email_body, "html.parser")
            email_body = soup.get_text()

        for pattern in patterns:
            try:
                matches = re.finditer(pattern, email_body, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    result = match.group(1) if match.groups() else match.group(0)
                    if result not in results:
                        results.append(result)
            except Exception as e:
                self.logger.error(f"Regex error with pattern {pattern}: {e}")
                continue

        return results
