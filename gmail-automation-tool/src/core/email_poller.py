import asyncio
import time
from typing import Optional, List, Dict, Callable
import logging


class EmailPoller:
    def __init__(self, email_client, code_parser, ai_parser=None):
        self.email_client = email_client
        self.code_parser = code_parser
        self.ai_parser = ai_parser
        self.logger = logging.getLogger(__name__)

    async def poll_for_code(
        self,
        sender_patterns: List[str],
        subject_patterns: List[str],
        extraction_type: str,
        interval_seconds: int = 5,
        timeout_seconds: int = 60,
    ) -> Optional[str]:
        """Poll for verification code/URL in emails"""

        start_time = time.time()
        last_check_time = start_time

        self.logger.info(f"Starting email polling for {extraction_type}")

        while time.time() - start_time < timeout_seconds:
            try:
                # Build query for Gmail API
                query_parts = []

                # Add sender patterns
                if sender_patterns:
                    sender_query = " OR ".join(
                        [f"from:{pattern}" for pattern in sender_patterns]
                    )
                    query_parts.append(f"({sender_query})")

                # Add subject patterns
                if subject_patterns:
                    subject_query = " OR ".join(
                        [f"subject:{pattern}" for pattern in subject_patterns]
                    )
                    query_parts.append(f"({subject_query})")

                # Only get recent messages
                query_parts.append(f"after:{int(last_check_time)}")

                query = " AND ".join(query_parts)

                messages = self.email_client.get_recent_messages(
                    query=query, max_results=5
                )

                for message in messages:
                    self.logger.info(f"Checking message: {message['subject']}")

                    # Try standard regex parsing first
                    if extraction_type == "otp":
                        code = self.code_parser.extract_otp(message["body"])
                    elif extraction_type == "url":
                        code = self.code_parser.extract_url(message["body"])
                    else:
                        code = None

                    if code:
                        self.logger.info(f"Found {extraction_type}: {code}")
                        return code

                    # Try AI parsing if available and standard parsing failed
                    if self.ai_parser and not code:
                        code = await self.ai_parser.extract_code(
                            message["body"], extraction_type
                        )
                        if code:
                            self.logger.info(f"AI found {extraction_type}: {code}")
                            return code

                self.logger.debug(
                    f"No {extraction_type} found, waiting {interval_seconds}s..."
                )
                await asyncio.sleep(interval_seconds)

            except Exception as e:
                self.logger.error(f"Error during polling: {e}")
                await asyncio.sleep(interval_seconds)

        self.logger.warning(f"Polling timeout reached for {extraction_type}")
        return None

    async def poll_with_trigger(
        self,
        trigger_func: Callable,
        sender_patterns: List[str],
        subject_patterns: List[str],
        extraction_type: str,
        interval_seconds: int = 5,
        timeout_seconds: int = 60,
    ) -> Optional[str]:
        """Execute trigger action and then poll for code"""

        # Execute the trigger action
        self.logger.info("Executing trigger action...")
        await trigger_func()

        # Wait a bit for email to be sent
        await asyncio.sleep(2)

        # Start polling
        return await self.poll_for_code(
            sender_patterns,
            subject_patterns,
            extraction_type,
            interval_seconds,
            timeout_seconds,
        )
