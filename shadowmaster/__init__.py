"""
ShadowMaster Framework - Cross-Site Shadow DOM Automation
"""

__version__ = "1.0.0"
__author__ = "ShadowMaster Team"
__description__ = (
    "Robust Playwright-based automation framework for Shadow DOM interaction"
)

from core.browser_manager import BrowserManager
from core.shadow_helper import ShadowHelper
from pages.base_page import BasePage
from utils.page_factory import PageFactory

__all__ = ["BrowserManager", "ShadowHelper", "BasePage", "PageFactory"]
