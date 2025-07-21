"""
Gmail OTP/URL/Code Extraction Tool

An automated tool for extracting verification codes, URLs, and other codes
from Gmail emails with AI-enhanced parsing capabilities.
"""

__version__ = "1.0.0"
__author__ = "Email Automation Team"

# Import main classes for easy access
from .core.email_client import EmailClient
from .core.email_poller import EmailPoller
from .core.code_parser import CodeParser
from .core.trigger_actions import TriggerActions
from .utils.config import Config

__all__ = ["EmailClient", "EmailPoller", "CodeParser", "TriggerActions", "Config"]
