"""
Base Page Object for ShadowMaster Framework
Provides common functionality for all page objects.
"""

from typing import Dict, Any, Optional
from playwright.async_api import Page
from core.shadow_helper import ShadowHelper
from core.ai_selector import get_ai_selector
import logging
import asyncio

logger = logging.getLogger(__name__)


class BasePage:
    """Base class for all page objects with Shadow DOM support."""

    def __init__(self, page: Page, config: Dict[str, Any]):
        self.page = page
        self.config = config
        self.url = config.get("url", "")
        self.name = config.get("name", "Unknown")
        self.locators = config.get("locators", {})
        self.shadow_elements = config.get("shadow_elements", [])

        # Initialize helpers
        self.shadow_helper = ShadowHelper(page)
        self.ai_selector = get_ai_selector()

        # State tracking
        self._page_loaded = False
        self._shadow_utils_injected = False

    async def navigate(self, wait_for_load: bool = True) -> bool:
        """
        Navigate to the page URL.

        Args:
            wait_for_load: Whether to wait for page load completion

        Returns:
            True if navigation successful, False otherwise
        """
        try:
            logger.info(f"Navigating to {self.name}: {self.url}")

            # Navigate with network idle wait
            response = await self.page.goto(
                self.url,
                wait_until="networkidle" if wait_for_load else "domcontentloaded"
            )

            if response and response.ok:
                self._page_loaded = True
                logger.info(f"Successfully navigated to {self.name}")

                # Inject shadow utilities
                await self._inject_utilities()

                return True
            else:
                logger.error(f"Navigation failed for {self.name}: {response.status if response else 'No response'}")
                return False

        except Exception as e:
            logger.error(f"Error navigating to {self.name}: {e}")
            return False

    async def wait_for_page_ready(self, timeout: int = 30000) -> bool:
        """
        Wait for page to be in ready state with all critical elements loaded.

        Args:
            timeout: Timeout in milliseconds

        Returns:
            True if page is ready, False if timeout
        """
        try:
            # Wait for document ready state
            await self.page.wait_for_load_state("networkidle", timeout=timeout)

            # Wait for any critical elements to be visible
            critical_elements = self._get_critical_elements()
            for selector in critical_elements:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000, state="visible")
                    logger.debug(f"Critical element found: {selector}")
                except:
                    logger.debug(f"Critical element not found (optional): {selector}")

            logger.info(f"Page {self.name} is ready")
            return True

        except Exception as e:
            logger.warning(f"Page ready timeout for {self.name}: {e}")
            return False

    async def get_locator(self, element_name: str, use_ai: bool = False) -> str:
        """
        Get locator for an element, optionally using AI inference.

        Args:
            element_name: Name of the element in config
            use_ai: Whether to use AI for selector inference

        Returns:
            CSS selector or locator string
        """
        # First try configured locator
        if element_name in self.locators:
            return self.locators[element_name]

        # Try AI inference if enabled
        if use_ai and self.ai_selector:
            try:
                page_content = await self.page.content()
                recommendation = await self.ai_selector.get_best_locator(
                    page_content,
                    f"Find {element_name} element",
                    f"Page: {self.name}"
                )

                if recommendation and recommendation.confidence > 0.7:
                    logger.info(f"AI suggested locator for {element_name}: {recommendation.preferred}")
                    return recommendation.preferred

            except Exception as e:
                logger.warning(f"AI selector inference failed for {element_name}: {e}")

        # Fallback to element name as selector
        logger.warning(f"Using fallback selector for {element_name}")
        return f"[data-testid='{element_name}'], #{element_name}, .{element_name}"

    async def click_element(self, element_name: str, timeout: int = 10000) -> bool:
        """
        Click an element with fallback strategies.

        Args:
            element_name: Name of the element to click
            timeout: Timeout in milliseconds

        Returns:
            True if click successful, False otherwise
        """
        selector = await self.get_locator(element_name)

        try:
            # Try regular click first
            await self.page.click(selector, timeout=timeout)
            logger.info(f"Clicked element {element_name} using selector: {selector}")
            return True

        except Exception as e:
            logger.warning(f"Regular click failed for {element_name}: {e}")

            # Try force click
            try:
                await self.page.click(selector, force=True, timeout=timeout)
                logger.info(f"Force clicked element {element_name}")
                return True
            except Exception as e2:
                logger.error(f"Force click also failed for {element_name}: {e2}")
                return False

    async def fill_element(self, element_name: str, value: str, 
                          clear_first: bool = True, timeout: int = 10000) -> bool:
        """
        Fill an input element with value.

        Args:
            element_name: Name of the input element
            value: Value to fill
            clear_first: Whether to clear existing content first
            timeout: Timeout in milliseconds

        Returns:
            True if fill successful, False otherwise
        """
        selector = await self.get_locator(element_name)

        try:
            element = self.page.locator(selector)
            await element.wait_for(state="visible", timeout=timeout)

            if clear_first:
                await element.clear()

            await element.fill(value)
            logger.info(f"Filled element {element_name} with value: {value}")
            return True

        except Exception as e:
            logger.error(f"Error filling element {element_name}: {e}")
            return False

    async def handle_shadow_popup(self, popup_config: Dict[str, str]) -> bool:
        """
        Handle shadow DOM popup/modal.

        Args:
            popup_config: Dictionary with 'host' and 'inner' selectors

        Returns:
            True if popup handled successfully, False otherwise
        """
        host_selector = popup_config.get("host", "")
        inner_selector = popup_config.get("inner", "")

        if not host_selector or not inner_selector:
            logger.warning("Invalid popup configuration")
            return False

        try:
            # Check if popup exists
            popup_exists = await self.page.locator(host_selector).count() > 0
            if not popup_exists:
                logger.info("No popup found")
                return True

            # Try to close using shadow helper
            success = await self.shadow_helper.click_shadow_element(
                host_selector, inner_selector
            )

            if success:
                logger.info(f"Successfully closed shadow popup: {host_selector}")
                # Wait for popup to disappear
                await asyncio.sleep(1)
                return True
            else:
                logger.warning(f"Failed to close shadow popup: {host_selector}")
                return False

        except Exception as e:
            logger.error(f"Error handling shadow popup: {e}")
            return False

    async def discover_shadow_elements(self) -> Dict[str, Any]:
        """
        Discover all Shadow DOM elements on the current page.

        Returns:
            Dictionary with discovered shadow elements information
        """
        try:
            hosts = await self.shadow_helper.discover_shadow_hosts()

            discovery_info = {
                "page": self.name,
                "url": self.url,
                "shadow_hosts_found": len(hosts),
                "hosts": hosts,
                "timestamp": asyncio.get_event_loop().time()
            }

            logger.info(f"Discovered {len(hosts)} shadow hosts on {self.name}")
            return discovery_info

        except Exception as e:
            logger.error(f"Error discovering shadow elements: {e}")
            return {"error": str(e)}

    async def take_screenshot(self, name_suffix: str = "") -> str:
        """Take a screenshot of the current page."""
        try:
            from core.browser_manager import BrowserManager
            # This would normally be injected, but for demo purposes
            timestamp = int(asyncio.get_event_loop().time())
            filename = f"{self.name.lower().replace(' ', '_')}_{name_suffix}_{timestamp}.png"

            await self.page.screenshot(
                path=f"test-results/screenshots/{filename}",
                full_page=True
            )

            logger.info(f"Screenshot saved: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return ""

    async def _inject_utilities(self):
        """Inject Shadow DOM utilities and other helper scripts."""
        if not self._shadow_utils_injected:
            await self.shadow_helper.inject_shadow_piercing_utils()
            self._shadow_utils_injected = True

    def _get_critical_elements(self) -> list:
        """
        Get list of critical elements that should be present on the page.
        Override in subclasses to define page-specific critical elements.

        Returns:
            List of CSS selectors for critical elements
        """
        return ["body", "head"]

    async def cleanup(self):
        """Clean up page resources."""
        if hasattr(self, 'shadow_helper'):
            self.shadow_helper.clear_cache()

        logger.info(f"Cleaned up page object for {self.name}")
