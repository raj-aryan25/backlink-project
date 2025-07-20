"""
Page Factory for ShadowMaster Framework
Dynamically creates appropriate page objects based on site configuration.
"""

from typing import Dict, Any, Optional
from playwright.async_api import Page

from pages.base_page import BasePage
from pages.reddit_page import RedditPage
from pages.dasoertliche_page import DasOertlichePage
from pages.gelbeseiten_page import GelbeseitenPage

import logging

logger = logging.getLogger(__name__)


class PageFactory:
    """Factory class for creating page objects."""

    # Registry of available page classes
    PAGE_CLASSES = {
        "reddit": RedditPage,
        "dasoertliche": DasOertlichePage,
        "gelbeseiten": GelbeseitenPage
    }

    @classmethod
    def create_page(cls, site_name: str, page: Page, config: Dict[str, Any]) -> BasePage:
        """
        Create appropriate page object for the given site.

        Args:
            site_name: Name of the site (from config)
            page: Playwright page instance
            config: Site configuration dictionary

        Returns:
            Page object instance

        Raises:
            ValueError: If site_name is not supported
        """
        site_key = site_name.lower()

        if site_key in cls.PAGE_CLASSES:
            page_class = cls.PAGE_CLASSES[site_key]
            logger.info(f"Creating {page_class.__name__} for site: {site_name}")
            return page_class(page, config)
        else:
            # Fallback to base page for unknown sites
            logger.warning(f"Unknown site {site_name}, using BasePage")
            return BasePage(page, config)

    @classmethod
    def register_page_class(cls, site_name: str, page_class: type):
        """
        Register a new page class for a site.

        Args:
            site_name: Name of the site
            page_class: Page class to register
        """
        cls.PAGE_CLASSES[site_name.lower()] = page_class
        logger.info(f"Registered {page_class.__name__} for site: {site_name}")

    @classmethod
    def get_supported_sites(cls) -> list:
        """Get list of supported site names."""
        return list(cls.PAGE_CLASSES.keys())

    @classmethod
    def is_site_supported(cls, site_name: str) -> bool:
        """Check if a site is supported."""
        return site_name.lower() in cls.PAGE_CLASSES


# Convenience function
def create_page_for_site(site_name: str, page: Page, config: Dict[str, Any]) -> BasePage:
    """
    Convenience function to create a page object.

    Args:
        site_name: Name of the site
        page: Playwright page instance
        config: Site configuration

    Returns:
        Appropriate page object instance
    """
    return PageFactory.create_page(site_name, page, config)
