"""
Test suite for email automation tool.

Contains comprehensive tests for email processing, code extraction,
and web automation components.
"""

import logging
import os

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("email_tests.log")],
)


# Test utilities
def setup_email_test_environment():
    """Set up email testing environment"""
    os.environ.setdefault("PYTEST_CURRENT_TEST", "true")
    os.environ.setdefault("HEADLESS", "false")

    # Check for required credentials
    required_files = ["config/gmail_credentials.json", "config/config.yaml"]

    for file_path in required_files:
        if not os.path.exists(file_path):
            logging.warning(f"Required file not found: {file_path}")


def mock_email_client():
    """Create mock email client for testing"""
    # This would be implemented based on testing needs
    pass


__all__ = ["setup_email_test_environment", "mock_email_client"]
