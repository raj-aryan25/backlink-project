# browser_manager.py - FIXED VERSION
# This fixes the "record_trace_dir" error and enables visible browser mode

import asyncio
import os
from typing import Dict, Any, Optional
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)
import logging


class BrowserManager:
    """Enhanced browser management with visible mode support"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.logger = logging.getLogger(__name__)

    async def launch_browser(self, headless: bool = False, slow_mo: int = 1000):
        """Launch browser in visible or headless mode"""
        try:
            self.playwright = await async_playwright().start()

            # Browser launch options for better visibility and debugging
            launch_options = {
                "headless": headless,  # Set to False for visible mode
                "slow_mo": slow_mo,  # Slow down actions for visibility
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--window-size=1280,720",
                ],
            }

            # Launch browser
            self.browser = await self.playwright.chromium.launch(**launch_options)

            # Create context with proper settings - FIXED: Removed record_trace_dir
            context_options = {
                "viewport": {"width": 1280, "height": 720},
                "ignore_https_errors": True,
                "java_script_enabled": True,
                "accept_downloads": True,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }

            # Add video recording if specified - FIXED: Using correct parameter
            if self.config.get("record_video", False):
                os.makedirs("videos", exist_ok=True)
                context_options["record_video_dir"] = "videos"
                context_options["record_video_size"] = {"width": 1280, "height": 720}

            self.context = await self.browser.new_context(**context_options)

            # FIXED: Start tracing AFTER creating context
            if self.config.get("enable_tracing", False):
                os.makedirs("traces", exist_ok=True)
                await self.context.tracing.start(
                    screenshots=True, snapshots=True, sources=True
                )

            self.logger.info("✅ Browser launched successfully")
            return self.context

        except Exception as e:
            self.logger.error(f"❌ Failed to launch browser: {e}")
            raise

    async def create_page(self) -> Page:
        """Create a new page with enhanced settings"""
        if not self.context:
            raise RuntimeError("Browser context not initialized")

        page = await self.context.new_page()

        # Set longer timeouts for better reliability
        page.set_default_timeout(30000)  # 30 seconds
        page.set_default_navigation_timeout(60000)  # 60 seconds

        # Add console logging for debugging
        page.on("console", lambda msg: self.logger.info(f"Console: {msg.text}"))
        page.on("pageerror", lambda msg: self.logger.error(f"Page error: {msg}"))

        return page

    async def cleanup(self):
        """Clean up browser resources"""
        try:
            # FIXED: Stop tracing before closing context
            if self.context and self.config.get("enable_tracing", False):
                await self.context.tracing.stop(path="traces/trace.zip")

            if self.context:
                await self.context.close()

            if self.browser:
                await self.browser.close()

            if self.playwright:
                await self.playwright.stop()

            self.logger.info("✅ Browser cleanup completed")

        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
