"""
ShadowMaster Framework - Main Runner
Entry point for running cross-site Shadow DOM automation tests.
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from core.browser_manager import BrowserManager
from utils.page_factory import PageFactory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create logs directory
    Path("test-results/logs").mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test-results/logs/shadowmaster.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)


class ShadowMasterRunner:
    """Main runner class for ShadowMaster framework."""

    def __init__(self, headless: bool = True, enable_ai: bool = False):
        self.headless = headless
        self.enable_ai = enable_ai
        self.browser_manager = None
        self.results = {}

    async def run_single_site_test(self, site_name: str, test_scenario: str = "basic") -> dict:
        """
        Run test on a single site.

        Args:
            site_name: Name of the site to test
            test_scenario: Type of test scenario to run

        Returns:
            Dictionary with test results
        """
        logger.info(f"Running {test_scenario} test on {site_name}")

        try:
            # Get site configuration
            site_config = self.browser_manager.get_site_config(site_name)
            if not site_config:
                raise ValueError(f"No configuration found for site: {site_name}")

            # Create page
            page = await self.browser_manager.new_page(site_name)
            page_obj = PageFactory.create_page(site_name, page, site_config)

            # Run the test scenario
            if test_scenario == "basic":
                result = await self._run_basic_test(page_obj, site_name)
            elif test_scenario == "shadow_discovery":
                result = await self._run_shadow_discovery_test(page_obj, site_name)
            elif test_scenario == "interaction":
                result = await self._run_interaction_test(page_obj, site_name)
            else:
                raise ValueError(f"Unknown test scenario: {test_scenario}")

            await page_obj.cleanup()
            logger.info(f"Test completed for {site_name}: {result['status']}")
            return result

        except Exception as e:
            logger.error(f"Test failed for {site_name}: {e}")
            return {
                "site": site_name,
                "scenario": test_scenario,
                "status": "failed",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }

    async def _run_basic_test(self, page_obj, site_name: str) -> dict:
        """Run basic navigation and page load test."""
        result = {
            "site": site_name,
            "scenario": "basic",
            "status": "running",
            "steps": [],
            "timestamp": asyncio.get_event_loop().time()
        }

        # Step 1: Navigate to site
        logger.info(f"Step 1: Navigating to {site_name}")
        nav_success = await page_obj.navigate()
        result["steps"].append({
            "step": "navigation",
            "success": nav_success,
            "message": "Navigation successful" if nav_success else "Navigation failed"
        })

        if not nav_success:
            result["status"] = "failed"
            return result

        # Step 2: Wait for page ready
        logger.info(f"Step 2: Waiting for {site_name} to be ready")
        ready_success = await page_obj.wait_for_page_ready()
        result["steps"].append({
            "step": "page_ready",
            "success": ready_success,
            "message": "Page ready" if ready_success else "Page not ready"
        })

        # Step 3: Take screenshot
        logger.info(f"Step 3: Taking screenshot of {site_name}")
        screenshot = await page_obj.take_screenshot("basic_test")
        result["steps"].append({
            "step": "screenshot",
            "success": bool(screenshot),
            "screenshot": screenshot
        })

        result["status"] = "passed"
        return result

    async def _run_shadow_discovery_test(self, page_obj, site_name: str) -> dict:
        """Run shadow DOM discovery test."""
        result = {
            "site": site_name,
            "scenario": "shadow_discovery",
            "status": "running",
            "shadow_elements": [],
            "timestamp": asyncio.get_event_loop().time()
        }

        # Navigate first
        await page_obj.navigate()
        await page_obj.wait_for_page_ready()

        # Discover shadow elements
        logger.info(f"Discovering shadow elements on {site_name}")
        shadow_info = await page_obj.discover_shadow_elements()
        result["shadow_elements"] = shadow_info

        # Take screenshot
        await page_obj.take_screenshot("shadow_discovery")

        result["status"] = "passed"
        return result

    async def _run_interaction_test(self, page_obj, site_name: str) -> dict:
        """Run site-specific interaction test."""
        result = {
            "site": site_name,
            "scenario": "interaction",
            "status": "running",
            "interactions": [],
            "timestamp": asyncio.get_event_loop().time()
        }

        await page_obj.navigate()
        await page_obj.wait_for_page_ready()

        # Site-specific interactions
        if site_name == "reddit":
            interactions = await self._test_reddit_interactions(page_obj)
        elif site_name == "dasoertliche":
            interactions = await self._test_dasoertliche_interactions(page_obj)
        elif site_name == "gelbeseiten":
            interactions = await self._test_gelbeseiten_interactions(page_obj)
        else:
            interactions = ["No specific interactions defined for this site"]

        result["interactions"] = interactions
        result["status"] = "passed"
        return result

    async def _test_reddit_interactions(self, reddit_page) -> List[str]:
        """Test Reddit-specific interactions."""
        interactions = []

        try:
            # Test popup handling
            popup_handled = await reddit_page.handle_popups_and_overlays()
            interactions.append(f"Popup handling: {'Success' if popup_handled else 'No popups found'}")

            # Test search
            search_success = await reddit_page.search_subreddit("test")
            interactions.append(f"Search functionality: {'Working' if search_success else 'Failed'}")

        except Exception as e:
            interactions.append(f"Reddit interaction error: {e}")

        return interactions

    async def _test_dasoertliche_interactions(self, dasoertliche_page) -> List[str]:
        """Test Das Örtliche-specific interactions."""
        interactions = []

        try:
            # Test cookie banner
            cookie_handled = await dasoertliche_page.handle_cookie_banner()
            interactions.append(f"Cookie banner handling: {'Success' if cookie_handled else 'Failed'}")

            # Test search
            search_success = await dasoertliche_page.perform_search("Test", "Berlin")
            interactions.append(f"Search functionality: {'Working' if search_success else 'Failed'}")

        except Exception as e:
            interactions.append(f"Das Örtliche interaction error: {e}")

        return interactions

    async def _test_gelbeseiten_interactions(self, gelbeseiten_page) -> List[str]:
        """Test Gelbe Seiten-specific interactions."""
        interactions = []

        try:
            # Test consent manager
            consent_handled = await gelbeseiten_page.handle_consent_manager()
            interactions.append(f"Consent manager handling: {'Success' if consent_handled else 'Failed'}")

            # Test search
            search_success = await gelbeseiten_page.perform_business_search("Restaurant", "München")
            interactions.append(f"Business search: {'Working' if search_success else 'Failed'}")

        except Exception as e:
            interactions.append(f"Gelbe Seiten interaction error: {e}")

        return interactions

    async def run_cross_site_tests(self, sites: List[str], scenarios: List[str]) -> dict:
        """
        Run tests across multiple sites and scenarios.

        Args:
            sites: List of site names to test
            scenarios: List of test scenarios to run

        Returns:
            Dictionary with all test results
        """
        logger.info(f"Running cross-site tests on {len(sites)} sites with {len(scenarios)} scenarios")

        self.browser_manager = BrowserManager()
        await self.browser_manager.start(headless=self.headless)

        try:
            all_results = {
                "total_sites": len(sites),
                "total_scenarios": len(scenarios),
                "test_results": {},
                "summary": {}
            }

            for site in sites:
                site_results = {}
                for scenario in scenarios:
                    result = await self.run_single_site_test(site, scenario)
                    site_results[scenario] = result

                all_results["test_results"][site] = site_results

            # Generate summary
            all_results["summary"] = self._generate_summary(all_results["test_results"])

            return all_results

        finally:
            await self.browser_manager.stop()

    def _generate_summary(self, test_results: dict) -> dict:
        """Generate test summary statistics."""
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "sites_tested": list(test_results.keys()),
            "success_rate": 0.0
        }

        for site, scenarios in test_results.items():
            for scenario, result in scenarios.items():
                summary["total_tests"] += 1
                if result.get("status") == "passed":
                    summary["passed"] += 1
                else:
                    summary["failed"] += 1

        if summary["total_tests"] > 0:
            summary["success_rate"] = summary["passed"] / summary["total_tests"]

        return summary


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ShadowMaster Framework - Cross-Site Shadow DOM Testing")
    parser.add_argument("--sites", nargs="+", default=["reddit", "dasoertliche", "gelbeseiten"],
                       help="Sites to test")
    parser.add_argument("--scenarios", nargs="+", default=["basic", "shadow_discovery"],
                       help="Test scenarios to run")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Run in headless mode")
    parser.add_argument("--visible", action="store_true",
                       help="Run in visible mode (opposite of headless)")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    parser.add_argument("--enable-ai", action="store_true",
                       help="Enable AI-powered features")

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Determine headless mode
    headless = args.headless and not args.visible

    logger.info("Starting ShadowMaster Framework")
    logger.info(f"Sites to test: {args.sites}")
    logger.info(f"Scenarios: {args.scenarios}")
    logger.info(f"Headless mode: {headless}")
    logger.info(f"AI features: {'Enabled' if args.enable_ai else 'Disabled'}")

    try:
        # Create and run tests
        runner = ShadowMasterRunner(headless=headless, enable_ai=args.enable_ai)
        results = await runner.run_cross_site_tests(args.sites, args.scenarios)

        # Save results
        import json
        results_file = Path("test-results/shadowmaster_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Print summary
        summary = results["summary"]
        logger.info("\n" + "="*50)
        logger.info("TEST SUMMARY")
        logger.info("="*50)
        logger.info(f"Total tests run: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Success rate: {summary['success_rate']:.2%}")
        logger.info(f"Sites tested: {', '.join(summary['sites_tested'])}")
        logger.info(f"Results saved to: {results_file}")

        return 0 if summary["failed"] == 0 else 1

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
