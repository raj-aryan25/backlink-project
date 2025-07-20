"""
Das Örtliche Page Object for ShadowMaster Framework
Handles Das Örtliche specific interactions including Shadow DOM elements.
"""

from pages.base_page import BasePage
from typing import Dict, Any, List
import logging
import asyncio

logger = logging.getLogger(__name__)


class DasOertlichePage(BasePage):
    """Page object for Das Örtliche (German phone directory)."""

    def __init__(self, page, config: Dict[str, Any]):
        super().__init__(page, config)
        self.cookie_banner_handled = False

    def _get_critical_elements(self) -> list:
        """Critical elements that should be present on Das Örtliche."""
        return [
            "body",
            "header",
            "input[name='query'], input[placeholder*='Name'], .search-input"
        ]

    async def handle_cookie_banner(self) -> bool:
        """
        Handle the cookie consent banner which may be in Shadow DOM.

        Returns:
            True if banner handled successfully or not present, False on error
        """
        if self.cookie_banner_handled:
            return True

        try:
            # Common shadow DOM cookie banner configurations
            shadow_configs = [
                {
                    "host": "my-cookie-banner",
                    "inner": "button[aria-label='Schließen']"
                },
                {
                    "host": "cookie-consent",
                    "inner": ".accept-all"
                },
                {
                    "host": "consent-manager",
                    "inner": "button[data-accept='all']"
                }
            ]

            # Try regular cookie banners first
            regular_selectors = [
                "button:has-text('Akzeptieren')",
                "button:has-text('Alle akzeptieren')",
                "button:has-text('Zustimmen')",
                "#cookieAcceptButton",
                ".cookie-accept",
                "[data-testid='cookie-accept']"
            ]

            # Try regular selectors first
            for selector in regular_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector, timeout=3000)
                        logger.info(f"Handled cookie banner with regular selector: {selector}")
                        self.cookie_banner_handled = True
                        await asyncio.sleep(1)  # Wait for banner to disappear
                        return True
                except Exception:
                    continue

            # Try shadow DOM configurations
            for config in shadow_configs:
                try:
                    host_selector = config["host"]
                    inner_selector = config["inner"]

                    # Check if shadow host exists
                    if await self.page.locator(host_selector).count() > 0:
                        success = await self.shadow_helper.click_shadow_element(
                            host_selector, inner_selector
                        )

                        if success:
                            logger.info(f"Handled shadow cookie banner: {host_selector} -> {inner_selector}")
                            self.cookie_banner_handled = True
                            await asyncio.sleep(1)  # Wait for banner to disappear
                            return True

                except Exception as e:
                    logger.debug(f"Shadow config failed: {config} - {e}")
                    continue

            # If no cookie banner found, consider it handled
            logger.info("No cookie banner found or already dismissed")
            self.cookie_banner_handled = True
            return True

        except Exception as e:
            logger.error(f"Error handling cookie banner: {e}")
            return False

    async def perform_search(self, name: str, location: str = "") -> bool:
        """
        Perform a search on Das Örtliche.

        Args:
            name: Name or business to search for
            location: Optional location filter

        Returns:
            True if search initiated successfully, False otherwise
        """
        try:
            # First handle any popups
            await self.handle_cookie_banner()

            # Find and fill the search input
            search_filled = await self._fill_search_field(name)
            if not search_filled:
                logger.error("Could not fill search field")
                return False

            # Fill location if provided
            if location:
                location_filled = await self._fill_location_field(location)
                if not location_filled:
                    logger.warning("Could not fill location field, continuing anyway")

            # Submit the search
            search_submitted = await self._submit_search()
            if search_submitted:
                logger.info(f"Search submitted successfully for: {name}")
                return True
            else:
                logger.error("Could not submit search")
                return False

        except Exception as e:
            logger.error(f"Error performing search: {e}")
            return False

    async def _fill_search_field(self, name: str) -> bool:
        """Fill the main search field with fallback selectors."""
        search_selectors = [
            "input[name='query']",
            "input[name='name']",
            "input[placeholder*='Name' i]",
            "input[placeholder*='Suche' i]",
            ".search-input input",
            "#search-field",
            "[data-testid='search-input']"
        ]

        for selector in search_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)

                # Clear existing content
                await self.page.fill(selector, "")
                await self.page.fill(selector, name)

                # Verify the field was filled
                value = await self.page.input_value(selector)
                if value == name:
                    logger.info(f"Filled search field using selector: {selector}")
                    return True

            except Exception as e:
                logger.debug(f"Search selector failed: {selector} - {e}")
                continue

        return False

    async def _fill_location_field(self, location: str) -> bool:
        """Fill the location field with fallback selectors."""
        location_selectors = [
            "input[name='location']",
            "input[name='ort']",
            "input[placeholder*='Ort' i]",
            "input[placeholder*='Stadt' i]",
            "input[placeholder*='Location' i]",
            ".location-input input",
            "#location-field"
        ]

        for selector in location_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    await self.page.fill(selector, location)
                    logger.info(f"Filled location field using selector: {selector}")
                    return True
            except Exception:
                continue

        return False

    async def _submit_search(self) -> bool:
        """Submit the search form with fallback methods."""
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Suchen')",
            "button:has-text('Finden')",
            ".search-button",
            "[data-testid='search-submit']",
            ".btn-search"
        ]

        # Try clicking submit button
        for selector in submit_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    await self.page.click(selector)
                    logger.info(f"Submitted search using selector: {selector}")
                    return True
            except Exception:
                continue

        # Try pressing Enter in search field
        try:
            search_field = await self._get_active_search_field()
            if search_field:
                await search_field.press("Enter")
                logger.info("Submitted search using Enter key")
                return True
        except Exception as e:
            logger.debug(f"Enter key submission failed: {e}")

        return False

    async def _get_active_search_field(self):
        """Get the currently focused or main search field."""
        search_selectors = [
            "input[name='query']",
            "input[name='name']",
            ".search-input input"
        ]

        for selector in search_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    return self.page.locator(selector).first
            except Exception:
                continue

        return None

    async def handle_search_suggestions(self) -> bool:
        """
        Handle search suggestions dropdown that might appear.

        Returns:
            True if suggestions handled, False otherwise
        """
        try:
            suggestion_containers = [
                ".suggestions-dropdown",
                ".autocomplete-suggestions",
                "[data-testid='suggestions']",
                ".search-suggestions"
            ]

            for container in suggestion_containers:
                if await self.page.locator(container).count() > 0:
                    # Click first suggestion
                    first_suggestion = f"{container} li:first-child, {container} .suggestion:first-child"
                    try:
                        await self.page.click(first_suggestion, timeout=2000)
                        logger.info("Clicked first search suggestion")
                        return True
                    except Exception:
                        # Press Escape to close suggestions
                        await self.page.keyboard.press("Escape")
                        return True

            return False

        except Exception as e:
            logger.error(f"Error handling search suggestions: {e}")
            return False

    async def extract_search_results(self) -> List[Dict[str, Any]]:
        """
        Extract search results from the results page.

        Returns:
            List of dictionaries containing result information
        """
        try:
            # Wait for results to load
            await self.page.wait_for_selector(
                ".search-result, .result-item, [data-testid='result']",
                timeout=10000
            )

            results = []
            result_selectors = [
                ".search-result",
                ".result-item",
                ".listing",
                "[data-testid='result']"
            ]

            for selector in result_selectors:
                result_elements = await self.page.locator(selector).all()

                if result_elements:
                    for i, element in enumerate(result_elements[:10]):  # Limit to first 10
                        try:
                            # Extract basic information
                            name = await self._extract_text_from_element(element, [
                                ".name", ".title", "h2", "h3", ".business-name"
                            ])

                            address = await self._extract_text_from_element(element, [
                                ".address", ".location", ".addr"
                            ])

                            phone = await self._extract_text_from_element(element, [
                                ".phone", ".tel", "[href^='tel:']"
                            ])

                            result_data = {
                                "index": i + 1,
                                "name": name,
                                "address": address,
                                "phone": phone,
                                "selector_used": selector
                            }

                            results.append(result_data)

                        except Exception as e:
                            logger.debug(f"Error extracting result {i}: {e}")
                            continue

                    break  # If we found results, don't try other selectors

            logger.info(f"Extracted {len(results)} search results")
            return results

        except Exception as e:
            logger.error(f"Error extracting search results: {e}")
            return []

    async def _extract_text_from_element(self, element, selectors: List[str]) -> str:
        """Extract text from element using fallback selectors."""
        for selector in selectors:
            try:
                sub_element = element.locator(selector).first
                if await sub_element.count() > 0:
                    text = await sub_element.text_content()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue

        return ""

    async def handle_captcha_or_bot_protection(self) -> bool:
        """
        Handle CAPTCHA or bot protection mechanisms.

        Returns:
            True if handled or not present, False if blocked
        """
        try:
            # Check for common bot protection indicators
            protection_indicators = [
                "text='Bitte beweisen Sie, dass Sie ein Mensch sind'",
                ".captcha",
                "#captcha",
                ".bot-protection",
                "text='CAPTCHA'"
            ]

            for indicator in protection_indicators:
                if await self.page.locator(indicator).count() > 0:
                    logger.warning("Bot protection or CAPTCHA detected")
                    # Take a screenshot for debugging
                    await self.take_screenshot("captcha_detected")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking for bot protection: {e}")
            return False

    async def navigate_to_business_details(self, result_index: int = 0) -> bool:
        """
        Navigate to detailed business information page.

        Args:
            result_index: Index of the result to click (0-based)

        Returns:
            True if navigation successful, False otherwise
        """
        try:
            result_selectors = [
                f".search-result:nth-child({result_index + 1}) a",
                f".result-item:nth-child({result_index + 1}) .title-link",
                f".listing:nth-child({result_index + 1}) h2 a"
            ]

            for selector in result_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector)
                        logger.info(f"Clicked result {result_index} using selector: {selector}")

                        # Wait for new page to load
                        await self.page.wait_for_load_state("networkidle", timeout=10000)
                        return True

                except Exception:
                    continue

            logger.warning(f"Could not find clickable result at index {result_index}")
            return False

        except Exception as e:
            logger.error(f"Error navigating to business details: {e}")
            return False
