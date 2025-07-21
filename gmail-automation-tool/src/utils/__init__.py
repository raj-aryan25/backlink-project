"""
Utility modules for email automation tool.

Contains configuration management and helper utilities.
"""

from .config import Config, load_config

__all__ = ["Config", "load_config"]
