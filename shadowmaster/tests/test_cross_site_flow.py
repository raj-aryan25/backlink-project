"""
Cross-Site Shadow DOM Testing for ShadowMaster Framework
Tests all three websites: Reddit, Das Örtliche, and Gelbe Seiten
"""

import pytest
import asyncio
import logging
import json
import os
from pathlib import Path
from typing import Dict, Any

from core.browser_manager import BrowserManager
from core.shadow_helper import ShadowHelper
from pages.reddit_page import RedditPage
from pages.dasoertliche_page import DasOertlichePage
from pages.gelbeseiten_page import GelbeseitenPage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test-results/shadowmaster.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TestCrossSiteFlow:
    """Test class for cross-site Shadow DOM automation."""

    @pytest.fixture(scope="class")
    async def browser_manager(self):
        """Set up browser manager for all tests."""
        browser_mgr = BrowserManager()
        await browser_mgr.start(headless=os.getenv("HEADLESS", "true") == "true")
        yield browser_mgr
        await browser_mgr.stop()

    @pytest.fixture
    async def test_data(self):
        """Test data for various scenarios."""
        return {
            "reddit": {
                "test_email": "test@example.com",
                "test_username": "testuser123",
                "test_password": "TestPass123!",
                "search_query": "Python programming"
            },
            "dasoertliche": {
                "search_name": "Müller",
                "search_location": "Berlin",
                "business_name": "Bäckerei Schmidt"
            },
            "gelbeseiten": {
                "what_search": "Restaurant",
                "where_search": "München",
                "category_filter": "Pizza"
            }
        }

    @pytest.mark.asyncio
    async def test_reddit_shadow_dom_interaction(self, browser_manager, test_data):
        """Test Reddit login modal and form interactions."""
        logger.info("Starting Reddit Shadow DOM test")

        try:
            # Create page and Reddit page object
            page = await browser_manager.new_page("reddit")
            reddit_config = browser_manager.get_site_config("reddit")
            reddit_page = RedditPage(page, reddit_config)

            # Navigate to Reddit
            navigation_success = await reddit_page.navigate()
            assert navigation_success, "Failed to navigate to Reddit"

            # Wait for page to be ready
            await reddit_page.wait_for_page_ready()

            # Take initial screenshot
            await reddit_page.take_screenshot("initial_load")

            # Handle any popups first
            await reddit_page.handle_popups_and_overlays()

            # Discover shadow elements
            shadow_discovery = await reddit_page.discover_shadow_elements()
            logger.info(f"Reddit shadow discovery: {shadow_discovery}")

            # Test login modal opening
            login_opened = await reddit_page.open_login_modal()
            if login_opened:
                logger.info("Successfully opened Reddit login modal")
                await reddit_page.take_screenshot("login_modal_open")

                # Test switching to signup
                signup_switched = await reddit_page.switch_to_signup()
                if signup_switched:
                    logger.info("Successfully switched to signup form")
                    await reddit_page.take_screenshot("signup_form")

                    # Test email filling
                    email_filled = await reddit_page.fill_signup_email(
                        test_data["reddit"]["test_email"]
                    )
                    assert email_filled, "Failed to fill signup email"

                    await reddit_page.take_screenshot("email_filled")

                # Close modal
                await reddit_page.close_modal()

            # Test search functionality
            search_success = await reddit_page.search_subreddit(
                test_data["reddit"]["search_query"]
            )
            if search_success:
                logger.info("Search functionality working")
                await reddit_page.take_screenshot("search_results")

            logger.info("Reddit test completed successfully")

        except Exception as e:
            logger.error(f"Reddit test failed: {e}")
            await reddit_page.take_screenshot("error_state")
            raise
        finally:
            await reddit_page.cleanup()

    @pytest.mark.asyncio
    async def test_dasoertliche_shadow_cookie_banner(self, browser_manager, test_data):
        """Test Das Örtliche with Shadow DOM cookie banner."""
        logger.info("Starting Das Örtliche Shadow DOM test")

        try:
            # Create page and Das Örtliche page object
            page = await browser_manager.new_page("dasoertliche")
            dasoertliche_config = browser_manager.get_site_config("dasoertliche")
            dasoertliche_page = DasOertlichePage(page, dasoertliche_config)

            # Navigate to Das Örtliche
            navigation_success = await dasoertliche_page.navigate()
            assert navigation_success, "Failed to navigate to Das Örtliche"

            await dasoertliche_page.wait_for_page_ready()
            await dasoertliche_page.take_screenshot("initial_load")

            # Discover shadow elements
            shadow_discovery = await dasoertliche_page.discover_shadow_elements()
            logger.info(f"Das Örtliche shadow discovery: {shadow_discovery}")

            # Test shadow cookie banner handling
            cookie_handled = await dasoertliche_page.handle_cookie_banner()
            assert cookie_handled, "Failed to handle cookie banner"

            await dasoertliche_page.take_screenshot("cookies_handled")

            # Test search functionality
            search_success = await dasoertliche_page.perform_search(
                test_data["dasoertliche"]["search_name"],
                test_data["dasoertliche"]["search_location"]
            )

            if search_success:
                logger.info("Search submitted successfully")
                await dasoertliche_page.take_screenshot("search_submitted")

                # Wait for results and extract them
                await asyncio.sleep(3)
                results = await dasoertliche_page.extract_search_results()

                # Log results
                logger.info(f"Extracted {len(results)} search results")
                for result in results[:3]:  # Log first 3 results
                    logger.info(f"Result: {result}")

                await dasoertliche_page.take_screenshot("search_results")

            # Test bot protection handling
            bot_protection_ok = await dasoertliche_page.handle_captcha_or_bot_protection()
            if not bot_protection_ok:
                logger.warning("Bot protection detected")

            logger.info("Das Örtliche test completed successfully")

        except Exception as e:
            logger.error(f"Das Örtliche test failed: {e}")
            await dasoertliche_page.take_screenshot("error_state")
            raise
        finally:
            await dasoertliche_page.cleanup()

    @pytest.mark.asyncio
    async def test_gelbeseiten_consent_manager(self, browser_manager, test_data):
        """Test Gelbe Seiten with Shadow DOM consent manager."""
        logger.info("Starting Gelbe Seiten Shadow DOM test")

        try:
            # Create page and Gelbe Seiten page object
            page = await browser_manager.new_page("gelbeseiten")
            gelbeseiten_config = browser_manager.get_site_config("gelbeseiten")
            gelbeseiten_page = GelbeseitenPage(page, gelbeseiten_config)

            # Navigate to Gelbe Seiten
            navigation_success = await gelbeseiten_page.navigate()
            assert navigation_success, "Failed to navigate to Gelbe Seiten"

            await gelbeseiten_page.wait_for_page_ready()
            await gelbeseiten_page.take_screenshot("initial_load")

            # Discover shadow elements
            shadow_discovery = await gelbeseiten_page.discover_shadow_elements()
            logger.info(f"Gelbe Seiten shadow discovery: {shadow_discovery}")

            # Test shadow consent manager handling
            consent_handled = await gelbeseiten_page.handle_consent_manager()
            assert consent_handled, "Failed to handle consent manager"

            await gelbeseiten_page.take_screenshot("consent_handled")

            # Test business search functionality
            search_success = await gelbeseiten_page.perform_business_search(
                test_data["gelbeseiten"]["what_search"],
                test_data["gelbeseiten"]["where_search"]
            )

            if search_success:
                logger.info("Business search submitted successfully")
                await gelbeseiten_page.take_screenshot("search_submitted")

                # Wait for results
                await asyncio.sleep(5)

                # Handle any advertisement popups
                await gelbeseiten_page.handle_advertisement_popups()

                # Extract business listings
                businesses = await gelbeseiten_page.extract_business_listings()

                # Log results
                logger.info(f"Extracted {len(businesses)} business listings")
                for business in businesses[:3]:  # Log first 3 businesses
                    logger.info(f"Business: {business}")

                await gelbeseiten_page.take_screenshot("business_results")

                # Test category filtering
                if businesses:
                    category_filtered = await gelbeseiten_page.filter_results_by_category(
                        test_data["gelbeseiten"]["category_filter"]
                    )
                    if category_filtered:
                        await gelbeseiten_page.take_screenshot("category_filtered")

            logger.info("Gelbe Seiten test completed successfully")

        except Exception as e:
            logger.error(f"Gelbe Seiten test failed: {e}")
            await gelbeseiten_page.take_screenshot("error_state")
            raise
        finally:
            await gelbeseiten_page.cleanup()

    @pytest.mark.asyncio
    async def test_cross_site_shadow_discovery(self, browser_manager):
        """Test shadow DOM discovery across all sites."""
        logger.info("Starting cross-site shadow discovery test")

        sites = ["reddit", "dasoertliche", "gelbeseiten"]
        discovery_results = {}

        for site_name in sites:
            try:
                logger.info(f"Testing shadow discovery on {site_name}")

                # Create page
                page = await browser_manager.new_page(f"discovery_{site_name}")
                site_config = browser_manager.get_site_config(site_name)

                # Create appropriate page object
                if site_name == "reddit":
                    page_obj = RedditPage(page, site_config)
                elif site_name == "dasoertliche":
                    page_obj = DasOertlichePage(page, site_config)
                else:  # gelbeseiten
                    page_obj = GelbeseitenPage(page, site_config)

                # Navigate and discover
                await page_obj.navigate()
                await page_obj.wait_for_page_ready()

                # Discover shadow elements
                shadow_info = await page_obj.discover_shadow_elements()
                discovery_results[site_name] = shadow_info

                # Take screenshot
                await page_obj.take_screenshot(f"discovery_{site_name}")

                await page_obj.cleanup()

            except Exception as e:
                logger.error(f"Shadow discovery failed for {site_name}: {e}")
                discovery_results[site_name] = {"error": str(e)}

        # Save discovery results
        results_path = Path("test-results/shadow_discovery.json")
        results_path.parent.mkdir(parents=True, exist_ok=True)

        with open(results_path, "w") as f:
            json.dump(discovery_results, f, indent=2, default=str)

        logger.info(f"Shadow discovery results saved to {results_path}")
        logger.info(f"Discovery summary: {discovery_results}")

    @pytest.mark.asyncio
    async def test_shadow_helper_robustness(self, browser_manager):
        """Test the robustness of shadow helper across different scenarios."""
        logger.info("Testing Shadow Helper robustness")

        try:
            # Test with Das Örtliche (known to have shadow elements)
            page = await browser_manager.new_page("shadow_test")
            dasoertliche_config = browser_manager.get_site_config("dasoertliche")
            dasoertliche_page = DasOertlichePage(page, dasoertliche_config)

            await dasoertliche_page.navigate()
            await dasoertliche_page.wait_for_page_ready()

            shadow_helper = dasoertliche_page.shadow_helper

            # Test 1: Query non-existent shadow element (should handle gracefully)
            logger.info("Test 1: Querying non-existent shadow element")
            non_existent = await shadow_helper.query_shadow(
                "non-existent-host", "non-existent-inner"
            )
            assert non_existent is None, "Should return None for non-existent elements"

            # Test 2: Inject shadow utilities
            logger.info("Test 2: Injecting shadow utilities")
            await shadow_helper.inject_shadow_piercing_utils()

            # Test 3: Discover shadow hosts
            logger.info("Test 3: Discovering shadow hosts")
            hosts = await shadow_helper.discover_shadow_hosts()
            logger.info(f"Discovered {len(hosts)} shadow hosts")

            # Test 4: Cache functionality
            logger.info("Test 4: Testing cache functionality")
            shadow_helper.clear_cache()
            logger.info("Cache cleared successfully")

            # Test 5: Handle different shadow modes (if any exist)
            logger.info("Test 5: Testing with different shadow configurations")
            test_configs = [
                {"host": "my-cookie-banner", "inner": "button"},
                {"host": "consent-manager", "inner": ".accept-all"},
                {"host": "unknown-element", "inner": ".button"}
            ]

            for config in test_configs:
                try:
                    result = await shadow_helper.click_shadow_element(
                        config["host"], config["inner"], timeout=2000
                    )
                    logger.info(f"Shadow config {config}: {'Success' if result else 'Not found'}")
                except Exception as e:
                    logger.info(f"Shadow config {config} error: {e}")

            await dasoertliche_page.cleanup()
            logger.info("Shadow Helper robustness test completed")

        except Exception as e:
            logger.error(f"Shadow Helper robustness test failed: {e}")
            raise


# Pytest configuration and runners
@pytest.mark.parametrize("site", ["reddit", "dasoertliche", "gelbeseiten"])
@pytest.mark.asyncio
async def test_site_accessibility(site):
    """Test that each site is accessible and loads properly."""
    browser_mgr = BrowserManager()
    await browser_mgr.start()

    try:
        page = await browser_mgr.new_page(f"accessibility_{site}")
        site_config = browser_mgr.get_site_config(site)

        # Navigate to site
        response = await page.goto(site_config["url"])
        assert response.ok, f"Site {site} returned non-OK status: {response.status}"

        # Check if page loaded
        await page.wait_for_load_state("networkidle", timeout=30000)
        title = await page.title()
        assert title, f"Site {site} has no title"

        logger.info(f"Site {site} is accessible: {title}")

    finally:
        await browser_mgr.stop()


if __name__ == "__main__":
    """Run tests directly with pytest."""
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--capture=no",
        f"--html=test-results/report.html",
        "--self-contained-html"
    ])
