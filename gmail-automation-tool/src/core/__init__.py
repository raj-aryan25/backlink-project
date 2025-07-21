"""
Core components for email automation.

This package contains the main email processing classes:
- EmailClient: Gmail API client for fetching emails
- EmailPoller: Automated polling for verification emails
- CodeParser: Regex-based code extraction from emails
- TriggerActions: Web automation to trigger email verification
"""

from .email_client import EmailClient
from .email_poller import EmailPoller
from .code_parser import CodeParser
from .trigger_actions import TriggerActions

__all__ = ["EmailClient", "EmailPoller", "CodeParser", "TriggerActions"]
