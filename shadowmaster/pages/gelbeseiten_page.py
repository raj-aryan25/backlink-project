"""
Gelbe Seiten Page Object for ShadowMaster Framework
Handles Gelbe Seiten specific interactions including Shadow DOM elements.
"""

from pages.base_page import BasePage
from typing import Dict, Any, List
import logging
import asyncio

logger = logging.getLogger(__name__)


class GelbeseitenPage(BasePage):
    """Page object for Gelbe Seiten (German Yellow Pages)."""

    def __init__(self, page, config: Dict[str, Any]):
        super().__init__(page, config)
        self.consent_handled = False

    def _get_critical_elements(self) -> list:
        """Critical elements that should be present on Gelbe Seiten."""
        return [
            "body",
            "header",
            "input[placeholder*='suche'], input[name='what'], .search-input"
        ]

    async def handle_consent_manager(self) -> bool:
        """
        Handle the consent manager which is typically in Shadow DOM.

        Returns:
            True if consent handled successfully or not present, False on error
        """
        if self.consent_handled:
            return True

        try:
            # Shadow DOM consent manager configurations
            shadow_configs = [
                {
                    "host": "consent-manager",
                    "inner": ".accept-all"
                },
                {
                    "host": "consent-manager",
                    "inner": "button[data-action='accept-all']"
                },
                {
                    "host": "cookie-consent",
                    "inner": ".btn-accept-all"
                },
                {
                    "host": "gdpr-consent",
                    "inner": "[data-consent='all']"
                }
            ]

            # Regular consent selectors
            regular_selectors = [
                "button:has-text('Alle akzeptieren')",
                "button:has-text('Akzeptieren und weiter')",
                "button:has-text('Zustimmen')",
                ".consent-accept-all",
                "#acceptAllCookies",
                "[data-testid='accept-all']",
                ".cmp-accept-all"
            ]

            # Try regular selectors first
            for selector in regular_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector, timeout=3000)
                        logger.info(f"Handled consent with regular selector: {selector}")
                        self.consent_handled = True
                        await asyncio.sleep(2)  # Wait for consent UI to disappear
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
                        logger.info(f"Found consent shadow host: {host_selector}")

                        success = await self.shadow_helper.click_shadow_element(
                            host_selector, inner_selector, timeout=5000
                        )

                        if success:
                            logger.info(f"Handled shadow consent: {host_selector} -> {inner_selector}")
                            self.consent_handled = True
                            await asyncio.sleep(2)  # Wait for consent UI to disappear
                            return True
                        else:
                            # Try alternative inner selectors for this host
                            alternative_inners = [
                                "button", ".accept", "[data-accept]", ".btn-primary"
                            ]

                            for alt_inner in alternative_inners:
                                try:
                                    alt_success = await self.shadow_helper.click_shadow_element(
                                        host_selector, alt_inner, timeout=2000
                                    )
                                    if alt_success:
                                        logger.info(f"Handled consent with alternative: {host_selector} -> {alt_inner}")
                                        self.consent_handled = True
                                        await asyncio.sleep(2)
                                        return True
                                except Exception:
                                    continue

                except Exception as e:
                    logger.debug(f"Shadow consent config failed: {config} - {e}")
                    continue

            # Check if consent overlay still exists
            overlay_present = await self._check_consent_overlay_present()
            if not overlay_present:
                logger.info("No consent overlay found or already handled")
                self.consent_handled = True
                return True

            # Final attempt: try to discover and handle dynamically
            return await self._discover_and_handle_consent()

        except Exception as e:
            logger.error(f"Error handling consent manager: {e}")
            return False

    async def _check_consent_overlay_present(self) -> bool:
        """Check if consent overlay is still present on the page."""
        overlay_selectors = [
            ".consent-overlay",
            ".cookie-overlay",
            ".gdpr-overlay",
            "[data-testid='consent-overlay']",
            ".cmp-overlay"
        ]

        for selector in overlay_selectors:
            if await self.page.locator(selector).count() > 0:
                return True

        return False

    async def _discover_and_handle_consent(self) -> bool:
        """Discover consent elements dynamically and attempt to handle them."""
        try:
            # Discover all shadow hosts
            shadow_hosts = await self.shadow_helper.discover_shadow_hosts()

            for host_info in shadow_hosts:
                try:
                    host_selector = f"{host_info['tagName']}"
                    if host_info.get('id'):
                        host_selector = f"#{host_info['id']}"
                    elif host_info.get('className'):
                        host_selector = f".{host_info['className'].split()[0]}"

                    # Try common consent button selectors inside this shadow host
                    consent_inners = [
                        "button:has-text('Accept')",
                        "button:has-text('Akzeptieren')",
                        ".accept-all",
                        "[data-action='accept']",
                        "button[aria-label*='accept' i]"
                    ]

                    for inner in consent_inners:
                        success = await self.shadow_helper.click_shadow_element(
                            host_selector, inner, timeout=2000
                        )
                        if success:
                            logger.info(f"Dynamically handled consent: {host_selector} -> {inner}")
                            self.consent_handled = True
                            return True

                except Exception as e:
                    logger.debug(f"Dynamic consent attempt failed for host {host_info}: {e}")
                    continue

            logger.warning("Could not handle consent overlay")
            return False

        except Exception as e:
            logger.error(f"Error in dynamic consent discovery: {e}")
            return False

    async def perform_business_search(self, what: str, where: str) -> bool:
        """
        Perform a business search on Gelbe Seiten.

        Args:
            what: What to search for (business type, name, etc.)
            where: Where to search (city, postal code, etc.)

        Returns:
            True if search initiated successfully, False otherwise
        """
        try:
            # Handle consent first
            consent_handled = await self.handle_consent_manager()
            if not consent_handled:
                logger.warning("Consent not handled, continuing anyway")

            # Fill "what" field
            what_filled = await self._fill_what_field(what)
            if not what_filled:
                logger.error("Could not fill 'what' search field")
                return False

            # Fill "where" field
            where_filled = await self._fill_where_field(where)
            if not where_filled:
                logger.error("Could not fill 'where' search field")
                return False

            # Submit search
            search_submitted = await self._submit_business_search()
            if search_submitted:
                logger.info(f"Business search submitted: '{what}' in '{where}'")
                return True
            else:
                logger.error("Could not submit business search")
                return False

        except Exception as e:
            logger.error(f"Error performing business search: {e}")
            return False

    async def _fill_what_field(self, what: str) -> bool:
        """Fill the 'what' search field with fallback selectors."""
        what_selectors = [
            "input[name='what']",
            "input[placeholder*='suche' i]",
            "input[placeholder*='was' i]",
            "input[data-testid='what-input']",
            ".search-what input",
            "#what-field",
            ".what-input"
        ]

        for selector in what_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)

                # Clear and fill
                await self.page.fill(selector, "")
                await self.page.fill(selector, what)

                # Verify
                value = await self.page.input_value(selector)
                if value == what:
                    logger.info(f"Filled 'what' field using selector: {selector}")
                    return True

            except Exception as e:
                logger.debug(f"'What' selector failed: {selector} - {e}")
                continue

        return False

    async def _fill_where_field(self, where: str) -> bool:
        """Fill the 'where' search field with fallback selectors."""
        where_selectors = [
            "input[name='where']",
            "input[placeholder*='Ort' i]",
            "input[placeholder*='wo' i]",
            "input[data-testid='where-input']",
            ".search-where input",
            "#where-field",
            ".where-input"
        ]

        for selector in where_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    await self.page.fill(selector, where)
                    logger.info(f"Filled 'where' field using selector: {selector}")
                    return True
            except Exception as e:
                logger.debug(f"'Where' selector failed: {selector} - {e}")
                continue

        return False

    async def _submit_business_search(self) -> bool:
        """Submit the business search form."""
        submit_selectors = [
            "button[data-testid='search-button']",
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Finden')",
            "button:has-text('Suchen')",
            ".search-submit",
            ".btn-search",
            "[data-testid='submit-search']"
        ]

        for selector in submit_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    await self.page.click(selector)
                    logger.info(f"Submitted search using selector: {selector}")
                    return True
            except Exception:
                continue

        # Try Enter key in what field
        try:
            what_field = await self._get_what_field()
            if what_field:
                await what_field.press("Enter")
                logger.info("Submitted search using Enter key")
                return True
        except Exception as e:
            logger.debug(f"Enter submission failed: {e}")

        return False

    async def _get_what_field(self):
        """Get the 'what' search field element."""
        what_selectors = [
            "input[name='what']",
            "input[placeholder*='suche' i]",
            ".search-what input"
        ]

        for selector in what_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    return self.page.locator(selector).first
            except Exception:
                continue

        return None

    async def extract_business_listings(self) -> List[Dict[str, Any]]:
        """
        Extract business listings from search results.

        Returns:
            List of dictionaries containing business information
        """
        try:
            # Wait for results to load
            await self.page.wait_for_selector(
                ".gs-result, .result-item, .listing, [data-testid='business-result']",
                timeout=15000
            )

            businesses = []
            result_selectors = [
                ".gs-result",
                ".result-item",
                ".business-listing",
                ".listing",
                "[data-testid='business-result']"
            ]

            for selector in result_selectors:
                result_elements = await self.page.locator(selector).all()

                if result_elements:
                    logger.info(f"Found {len(result_elements)} results with selector: {selector}")

                    for i, element in enumerate(result_elements[:15]):  # Limit to first 15
                        try:
                            business_data = await self._extract_business_data(element, i + 1)
                            if business_data:
                                businesses.append(business_data)

                        except Exception as e:
                            logger.debug(f"Error extracting business {i}: {e}")
                            continue

                    break  # Use first successful selector

            logger.info(f"Extracted {len(businesses)} business listings")
            return businesses

        except Exception as e:
            logger.error(f"Error extracting business listings: {e}")
            return []

    async def _extract_business_data(self, element, index: int) -> Dict[str, Any]:
        """Extract data from a single business listing element."""
        try:
            # Business name
            name = await self._extract_text_from_element(element, [
                ".gs-title", ".business-name", "h2", "h3", 
                ".title", "[data-testid='business-name']"
            ])

            # Address
            address = await self._extract_text_from_element(element, [
                ".gs-address", ".address", ".location", 
                "[data-testid='address']", ".street-address"
            ])

            # Phone number
            phone = await self._extract_text_from_element(element, [
                ".gs-phone", ".phone", ".tel", "[href^='tel:']",
                "[data-testid='phone']"
            ])

            # Website
            website = await self._extract_href_from_element(element, [
                ".gs-website", ".website", "[data-testid='website']",
                "a[href^='http']"
            ])

            # Rating
            rating = await self._extract_text_from_element(element, [
                ".rating", ".stars", "[data-testid='rating']", ".review-score"
            ])

            # Category
            category = await self._extract_text_from_element(element, [
                ".gs-category", ".category", ".business-type",
                "[data-testid='category']"
            ])

            return {
                "index": index,
                "name": name,
                "address": address,
                "phone": phone,
                "website": website,
                "rating": rating,
                "category": category,
                "has_data": bool(name or address or phone)
            }

        except Exception as e:
            logger.debug(f"Error extracting business data: {e}")
            return {}

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

    async def _extract_href_from_element(self, element, selectors: List[str]) -> str:
        """Extract href attribute from element using fallback selectors."""
        for selector in selectors:
            try:
                sub_element = element.locator(selector).first
                if await sub_element.count() > 0:
                    href = await sub_element.get_attribute("href")
                    if href and href.strip():
                        return href.strip()
            except Exception:
                continue

        return ""

    async def handle_advertisement_popups(self) -> bool:
        """
        Handle advertisement popups that might appear.

        Returns:
            True if popups handled or not present, False on error
        """
        try:
            popup_selectors = [
                ".ad-popup .close",
                ".advertisement-close",
                "[data-testid='close-ad']",
                ".modal-close",
                "button[aria-label*='close' i]",
                ".overlay-close"
            ]

            handled_any = False

            for selector in popup_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector, timeout=2000)
                        logger.info(f"Closed popup using selector: {selector}")
                        handled_any = True
                        await asyncio.sleep(1)
                except Exception:
                    continue

            # Try Escape key as fallback
            if not handled_any:
                await self.page.keyboard.press("Escape")
                handled_any = True

            return True

        except Exception as e:
            logger.error(f"Error handling advertisement popups: {e}")
            return False

    async def filter_results_by_category(self, category: str) -> bool:
        """
        Apply category filter to search results.

        Args:
            category: Category to filter by

        Returns:
            True if filter applied successfully, False otherwise
        """
        try:
            # Look for category filter elements
            filter_selectors = [
                f"text='{category}'",
                f"[data-category='{category}']",
                f".filter-category:has-text('{category}')",
                f".category-filter[value='{category}']"
            ]

            for selector in filter_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector)
                        logger.info(f"Applied category filter: {category}")

                        # Wait for results to update
                        await asyncio.sleep(2)
                        return True
                except Exception:
                    continue

            logger.warning(f"Could not find category filter for: {category}")
            return False

        except Exception as e:
            logger.error(f"Error filtering by category: {e}")
            return False
