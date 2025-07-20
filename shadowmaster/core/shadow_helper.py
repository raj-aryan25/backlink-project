"""
Shadow DOM Helper for ShadowMaster Framework
Universal API for discovering, piercing, and interacting with Shadow DOM elements.
"""

from typing import Optional, List, Dict, Any
from playwright.async_api import Page, ElementHandle, Locator
import asyncio
import logging

logger = logging.getLogger(__name__)


class ShadowDOMError(Exception):
    """Custom exception for Shadow DOM related errors."""
    pass


class ShadowHelper:
    """Helper class for Shadow DOM operations."""

    def __init__(self, page: Page):
        self.page = page
        self.shadow_roots_cache: Dict[str, ElementHandle] = {}

    async def query_shadow(self, host_selector: str, inner_selector: str, 
                          timeout: int = 5000) -> Optional[ElementHandle]:
        """
        Query an element inside a Shadow DOM.

        Args:
            host_selector: CSS selector for the shadow host element
            inner_selector: CSS selector for the element inside shadow DOM
            timeout: Timeout in milliseconds

        Returns:
            ElementHandle if found, None otherwise
        """
        try:
            # Wait for host element
            await self.page.wait_for_selector(host_selector, timeout=timeout)

            # Get shadow root
            shadow_root = await self._get_shadow_root(host_selector)
            if not shadow_root:
                logger.warning(f"Shadow root not found for host: {host_selector}")
                return None

            # Query inside shadow DOM
            element = await shadow_root.query_selector(inner_selector)
            return element

        except Exception as e:
            logger.error(f"Error querying shadow DOM: {e}")
            return None

    async def query_shadow_all(self, host_selector: str, inner_selector: str,
                              timeout: int = 5000) -> List[ElementHandle]:
        """Query all elements inside a Shadow DOM."""
        try:
            await self.page.wait_for_selector(host_selector, timeout=timeout)
            shadow_root = await self._get_shadow_root(host_selector)

            if not shadow_root:
                return []

            elements = await shadow_root.query_selector_all(inner_selector)
            return elements

        except Exception as e:
            logger.error(f"Error querying shadow DOM (all): {e}")
            return []

    async def click_shadow_element(self, host_selector: str, inner_selector: str,
                                  timeout: int = 5000) -> bool:
        """Click an element inside Shadow DOM."""
        element = await self.query_shadow(host_selector, inner_selector, timeout)
        if element:
            try:
                await element.click()
                logger.info(f"Clicked shadow element: {host_selector} -> {inner_selector}")
                return True
            except Exception as e:
                logger.error(f"Error clicking shadow element: {e}")
                return False
        return False

    async def fill_shadow_input(self, host_selector: str, inner_selector: str,
                               value: str, timeout: int = 5000) -> bool:
        """Fill an input element inside Shadow DOM."""
        element = await self.query_shadow(host_selector, inner_selector, timeout)
        if element:
            try:
                await element.fill(value)
                logger.info(f"Filled shadow input: {host_selector} -> {inner_selector}")
                return True
            except Exception as e:
                logger.error(f"Error filling shadow input: {e}")
                return False
        return False

    async def get_shadow_text(self, host_selector: str, inner_selector: str,
                             timeout: int = 5000) -> Optional[str]:
        """Get text content from Shadow DOM element."""
        element = await self.query_shadow(host_selector, inner_selector, timeout)
        if element:
            try:
                text = await element.text_content()
                return text
            except Exception as e:
                logger.error(f"Error getting shadow text: {e}")
        return None

    async def pierce_nested_shadow(self, shadow_path: List[Dict[str, str]],
                                  timeout: int = 5000) -> Optional[ElementHandle]:
        """Pierce through nested Shadow DOM structures."""
        current_root = None

        for i, path_item in enumerate(shadow_path):
            host_selector = path_item['host']

            if i == 0:
                # First level - query from page
                current_root = await self._get_shadow_root(host_selector)
            else:
                # Nested levels - query from current shadow root
                if current_root:
                    host_element = await current_root.query_selector(host_selector)
                    if host_element:
                        current_root = await host_element.evaluate_handle("e => e.shadowRoot")
                    else:
                        return None
                else:
                    return None

            if not current_root:
                logger.warning(f"Shadow root not found at level {i}: {host_selector}")
                return None

        # Get final element if target selector is provided
        final_path = shadow_path[-1]
        if 'target' in final_path:
            return await current_root.query_selector(final_path['target'])

        return current_root

    async def discover_shadow_hosts(self) -> List[Dict[str, Any]]:
        """Discover all Shadow DOM host elements on the page."""
        js_code = """
        () => {
            const hosts = [];
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_ELEMENT,
                {
                    acceptNode: function(node) {
                        return node.shadowRoot ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
                    }
                }
            );

            let node;
            while (node = walker.nextNode()) {
                hosts.push({
                    tagName: node.tagName.toLowerCase(),
                    id: node.id || null,
                    className: node.className || null,
                    shadowMode: node.shadowRoot.mode
                });
            }

            return hosts;
        }
        """

        try:
            hosts = await self.page.evaluate(js_code)
            logger.info(f"Discovered {len(hosts)} shadow hosts")
            return hosts
        except Exception as e:
            logger.error(f"Error discovering shadow hosts: {e}")
            return []

    async def inject_shadow_piercing_utils(self):
        """Inject utility functions for advanced Shadow DOM handling."""
        js_utils = """
        window.shadowUtils = {
            openShadow: function(element) {
                if (element.shadowRoot) {
                    return element.shadowRoot;
                }
                return null;
            },

            deepQuery: function(selector) {
                const elements = [];

                function traverse(root) {
                    const found = root.querySelectorAll(selector);
                    elements.push(...found);

                    const shadowHosts = root.querySelectorAll('*');
                    for (const host of shadowHosts) {
                        if (host.shadowRoot) {
                            traverse(host.shadowRoot);
                        }
                    }
                }

                traverse(document);
                return elements;
            }
        };
        """

        await self.page.add_init_script(js_utils)
        logger.info("Injected shadow piercing utilities")

    async def _get_shadow_root(self, host_selector: str) -> Optional[ElementHandle]:
        """Get shadow root for a host element."""
        # Check cache first
        if host_selector in self.shadow_roots_cache:
            return self.shadow_roots_cache[host_selector]

        try:
            host_element = await self.page.wait_for_selector(host_selector)
            shadow_root = await host_element.evaluate_handle("e => e.shadowRoot")

            if shadow_root:
                # Cache the shadow root
                self.shadow_roots_cache[host_selector] = shadow_root
                return shadow_root
            else:
                logger.warning(f"Shadow root is null for host: {host_selector}")
                return None

        except Exception as e:
            logger.error(f"Error getting shadow root for {host_selector}: {e}")
            return None

    def clear_cache(self):
        """Clear the shadow roots cache."""
        self.shadow_roots_cache.clear()
        logger.info("Cleared shadow roots cache")


# Convenience functions for direct use
async def query_shadow(page: Page, host_selector: str, inner_selector: str, 
                      timeout: int = 5000) -> Optional[ElementHandle]:
    """Convenience function to query Shadow DOM element."""
    helper = ShadowHelper(page)
    return await helper.query_shadow(host_selector, inner_selector, timeout)


async def click_shadow_element(page: Page, host_selector: str, inner_selector: str,
                              timeout: int = 5000) -> bool:
    """Convenience function to click Shadow DOM element."""
    helper = ShadowHelper(page)
    return await helper.click_shadow_element(host_selector, inner_selector, timeout)
