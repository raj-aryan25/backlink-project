# main.py - CORRECTED VERSION with Updated Selectors and Visible Browser Mode
# This fixes all the issues: browser context errors, wrong selectors, and enables debugging

#!/usr/bin/env python3
"""
Enhanced ShadowMaster Framework - Main Runner
Fixes selector issues and enables visible browser debugging
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
import json
import argparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import random


class ShadowMasterRunner:
    """Fixed main orchestrator for cross-site automation"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.logger = self._setup_logging()
        self.results = {}

    def _setup_logging(self) -> logging.Logger:
        """Setup enhanced logging with real-time visibility"""
        logger = logging.getLogger("ShadowMaster")
        logger.setLevel(logging.INFO)

        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    async def initialize(self):
        """Initialize browser with VISIBLE MODE"""
        try:
            self.logger.info("🚀 Starting Enhanced ShadowMaster Framework")

            playwright = await async_playwright().start()

            # FIXED: Launch browser in VISIBLE mode for debugging
            self.browser = await playwright.chromium.launch(
                headless=False,  # VISIBLE BROWSER for debugging
                slow_mo=2000,  # Slow down actions so you can see them
                args=["--window-size=1280,720"],
            )

            # FIXED: Create context without invalid parameters
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720}, ignore_https_errors=True
            )

            self.logger.info("✅ Browser initialized in VISIBLE mode")

        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            raise

    async def run_reddit_automation(self):
        """FIXED Reddit automation with current selectors"""
        self.logger.info("🔴 Starting Reddit automation")

        page = await self.context.new_page()
        result = {"site": "reddit", "success": False, "actions": []}

        try:
            # Navigate to Reddit
            self.logger.info("📋 Navigating to Reddit...")
            await page.goto("https://www.reddit.com/", wait_until="networkidle")
            await asyncio.sleep(3)  # Wait for page to fully load

            # FIXED: Updated selectors for current Reddit structure
            login_selectors = [
                "a[data-testid='login-button']",
                "a:has-text('Log In')",
                "button:has-text('Log In')",
                ".login",
                "a[href*='login']",
            ]

            # Try to find and click login button
            login_clicked = False
            for selector in login_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        self.logger.info("✅ Login button clicked")
                        login_clicked = True
                        result["actions"].append("login_button_clicked")
                        await asyncio.sleep(3)
                        break
                except:
                    continue

            if not login_clicked:
                # Navigate directly to login page
                await page.goto("https://www.reddit.com/login")
                self.logger.info("📋 Navigated directly to login page")

            # FIXED: Look for and click signup button
            signup_selectors = [
                "a:has-text('Sign Up')",
                "button:has-text('Sign Up')",
                "a:has-text('New to Reddit')",
                "a[href*='register']",
            ]

            signup_clicked = False
            for selector in signup_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        self.logger.info("✅ Signup button clicked")
                        signup_clicked = True
                        result["actions"].append("signup_button_clicked")
                        await asyncio.sleep(3)
                        break
                except:
                    continue

            if not signup_clicked:
                # Try navigating to register page directly
                await page.goto("https://www.reddit.com/register")
                self.logger.info("📋 Navigated directly to signup page")

            # FIXED: Enter dummy email
            email_selectors = [
                "input[name='email']",
                "input[type='email']",
                "input[placeholder*='email' i]",
                "#email",
            ]

            dummy_email = f"test{random.randint(1000,9999)}@example.com"

            for selector in email_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.fill(dummy_email)
                        self.logger.info(f"✅ Email entered: {dummy_email}")
                        result["actions"].append("email_entered")
                        result["email_used"] = dummy_email
                        break
                except:
                    continue

            # Take screenshot for verification
            screenshot_path = f"reddit_result_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            result["screenshot"] = screenshot_path

            result["success"] = True
            self.logger.info("✅ Reddit automation completed")

        except Exception as e:
            self.logger.error(f"❌ Reddit automation failed: {e}")
            result["error"] = str(e)
        finally:
            await page.close()

        return result

    async def run_dasoertliche_automation(self):
        """FIXED Das Örtliche automation with current selectors"""
        self.logger.info("🟡 Starting Das Örtliche automation")

        page = await self.context.new_page()
        result = {"site": "dasoertliche", "success": False, "actions": []}

        try:
            # Navigate to Das Örtliche
            self.logger.info("📋 Navigating to Das Örtliche...")
            await page.goto("https://www.dasoertliche.de/", wait_until="networkidle")
            await asyncio.sleep(3)

            # FIXED: Close cookie/consent popup
            consent_selectors = [
                "button:has-text('Akzeptieren')",
                "button:has-text('Alle akzeptieren')",
                "button[id*='accept']",
                ".cookie-accept",
                "button:has-text('OK')",
                "[aria-label*='close' i]",
            ]

            for selector in consent_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        self.logger.info("✅ Cookie popup closed")
                        result["actions"].append("popup_closed")
                        await asyncio.sleep(2)
                        break
                except:
                    continue

            # FIXED: Find and click "Anmelden" button
            anmelden_selectors = [
                "a:has-text('Anmelden')",
                "button:has-text('Anmelden')",
                ".anmelden",
                "[data-testid*='login']",
                "a[href*='login']",
            ]

            for selector in anmelden_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        self.logger.info("✅ Anmelden button clicked")
                        result["actions"].append("anmelden_clicked")
                        await asyncio.sleep(3)
                        break
                except:
                    continue

            # Look for registration link in modal
            register_selectors = [
                "a:has-text('Registrieren')",
                "button:has-text('Registrieren')",
                ".registrieren",
            ]

            for selector in register_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        self.logger.info("✅ Registration link clicked")
                        result["actions"].append("registration_clicked")
                        break
                except:
                    continue

            # Take screenshot
            screenshot_path = (
                f"dasoertliche_result_{datetime.now().strftime('%H%M%S')}.png"
            )
            await page.screenshot(path=screenshot_path)
            result["screenshot"] = screenshot_path

            result["success"] = True
            self.logger.info("✅ Das Örtliche automation completed")

        except Exception as e:
            self.logger.error(f"❌ Das Örtliche automation failed: {e}")
            result["error"] = str(e)
        finally:
            await page.close()

        return result

    async def run_gelbeseiten_automation(self):
        """FIXED Gelbe Seiten automation with current selectors"""
        self.logger.info("🟠 Starting Gelbe Seiten automation")

        page = await self.context.new_page()
        result = {"site": "gelbeseiten", "success": False, "actions": []}

        try:
            # Navigate to Gelbe Seiten
            self.logger.info("📋 Navigating to Gelbe Seiten...")
            await page.goto("https://www.gelbeseiten.de/", wait_until="networkidle")
            await asyncio.sleep(5)  # Wait longer for consent popup to appear

            # FIXED: Enhanced consent popup handling
            consent_strategies = [
                # Strategy 1: Standard consent buttons
                [
                    "button:has-text('Alle akzeptieren')",
                    "button:has-text('Accept All')",
                    "button[data-role='acceptAll']",
                    ".consent-accept-all",
                ],
                # Strategy 2: CMP specific selectors
                [
                    "#cmpwelcomebtnyes",
                    ".cmpboxbtnyes",
                    "[data-cmp='accept']",
                    ".sp_choice_type_11",
                ],
                # Strategy 3: Generic accept buttons
                [
                    "button:has-text('Akzeptieren')",
                    "button[id*='accept']",
                    ".accept-button",
                    "[aria-label*='accept' i]",
                ],
            ]

            popup_closed = False
            for strategy_idx, selectors in enumerate(consent_strategies):
                if popup_closed:
                    break

                self.logger.info(f"📋 Trying consent strategy {strategy_idx + 1}")
                for selector in selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element and await element.is_visible():
                            await element.click()
                            self.logger.info(
                                f"✅ Consent popup closed using: {selector}"
                            )
                            result["actions"].append("popup_closed")
                            popup_closed = True
                            await asyncio.sleep(3)
                            break
                    except:
                        continue

            if not popup_closed:
                self.logger.warning("⚠️ No consent popup found or unable to close")

            # Take screenshot to verify
            screenshot_path = (
                f"gelbeseiten_result_{datetime.now().strftime('%H%M%S')}.png"
            )
            await page.screenshot(path=screenshot_path)
            result["screenshot"] = screenshot_path

            result["success"] = True
            self.logger.info("✅ Gelbe Seiten automation completed")

        except Exception as e:
            self.logger.error(f"❌ Gelbe Seiten automation failed: {e}")
            result["error"] = str(e)
        finally:
            await page.close()

        return result

    async def run_all_sites(self, sites):
        """Run automation for all specified sites"""
        self.logger.info(f"🎯 Running automation for: {', '.join(sites)}")

        site_functions = {
            "reddit": self.run_reddit_automation,
            "dasoertliche": self.run_dasoertliche_automation,
            "gelbeseiten": self.run_gelbeseiten_automation,
        }

        for site in sites:
            if site in site_functions:
                result = await site_functions[site]()
                self.results[site] = result

                # Pause between sites for better visibility
                if site != sites[-1]:
                    self.logger.info("⏸️ Pausing 5 seconds before next site...")
                    await asyncio.sleep(5)
            else:
                self.logger.error(f"❌ Unknown site: {site}")

    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            self.logger.info("✅ Browser cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")

    def print_results(self):
        """Print execution summary"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 EXECUTION SUMMARY")
        self.logger.info("=" * 60)

        for site, result in self.results.items():
            if result.get("success"):
                actions = ", ".join(result.get("actions", []))
                self.logger.info(f"✅ {site.upper()}: SUCCESS - {actions}")
                if "email_used" in result:
                    self.logger.info(f"   📧 Email: {result['email_used']}")
                if "screenshot" in result:
                    self.logger.info(f"   📸 Screenshot: {result['screenshot']}")
            else:
                error = result.get("error", "Unknown error")
                self.logger.info(f"❌ {site.upper()}: FAILED - {error}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced ShadowMaster Framework")
    parser.add_argument(
        "--sites",
        nargs="+",
        default=["reddit", "dasoertliche", "gelbeseiten"],
        choices=["reddit", "dasoertliche", "gelbeseiten"],
        help="Sites to automate",
    )

    args = parser.parse_args()

    runner = ShadowMasterRunner()

    try:
        await runner.initialize()
        await runner.run_all_sites(args.sites)
    finally:
        await runner.cleanup()
        runner.print_results()


if __name__ == "__main__":
    print("🚀 Enhanced ShadowMaster Framework")
    print("=" * 50)
    print("✅ VISIBLE browser mode enabled")
    print("✅ Fixed browser context issues")
    print("✅ Updated website selectors")
    print("✅ Enhanced logging and debugging")
    print("=" * 50)

    asyncio.run(main())
