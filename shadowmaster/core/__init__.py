"""
Core components for ShadowMaster Framework
"""

from .browser_manager import BrowserManager
from .shadow_helper import ShadowHelper, ShadowDOMError
from .ai_selector import AISelector, SelectorRecommendation

__all__ = [
    "BrowserManager",
    "ShadowHelper",
    "ShadowDOMError",
    "AISelector",
    "SelectorRecommendation",
]
