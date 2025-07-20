"""
Browser Manager for ShadowMaster Framework
Handles Playwright browser lifecycle, configuration, and recording capabilities.
"""

import asyncio
import os
from typing import Dict, Any, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import yaml
from datetime import datetime


class BrowserManager:
    """Manages browser instances and configuration for cross-site testing."""

    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.pages: Dict[str, Page] = {}

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

    async def start(self, **browser_options) -> BrowserContext:
        """Start browser with configured options."""
        self.playwright = await async_playwright().start()

        # Merge config with runtime options
        launch_options = {
            "headless": browser_options.get("headless", self.config["browser"]["headless"]),
            "args": ["--disable-blink-features=AutomationControlled"],
        }

        self.browser = await self.playwright.chromium.launch(**launch_options)

        # Context options
        context_options = {
            "viewport": self.config["browser"]["viewport"],
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        # Add recording options if enabled
        if self.config["browser"].get("video_recording"):
            context_options["record_video_dir"] = "test-results/videos"

        if self.config["browser"].get("trace"):
            context_options["record_trace_dir"] = "test-results/traces"

        self.context = await self.browser.new_context(**context_options)

        # Start tracing if enabled
        if self.config["browser"].get("trace"):
            await self.context.tracing.start(screenshots=True, snapshots=True)

        return self.context

    async def new_page(self, site_name: str) -> Page:
        """Create a new page for a specific site."""
        if not self.context:
            raise RuntimeError("Browser context not started. Call start() first.")

        page = await self.context.new_page()

        # Set timeouts
        page.set_default_timeout(self.config["browser"]["timeout"])
        page.set_default_navigation_timeout(self.config["timeouts"]["page_load"])

        # Store page reference
        self.pages[site_name] = page

        return page

    async def take_screenshot(self, page: Page, name: str) -> str:
        """Take a screenshot and return the path."""
        if not self.config["browser"].get("screenshots"):
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = Path("test-results/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_dir / f"{name}_{timestamp}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        return str(screenshot_path)

    async def close_page(self, site_name: str):
        """Close a specific page."""
        if site_name in self.pages:
            await self.pages[site_name].close()
            del self.pages[site_name]

    async def stop(self):
        """Stop browser and clean up resources."""
        # Save trace if enabled
        if self.context and self.config["browser"].get("trace"):
            trace_path = f"test-results/traces/trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            await self.context.tracing.stop(path=trace_path)

        # Close all pages
        for page_name in list(self.pages.keys()):
            await self.close_page(page_name)

        # Close context and browser
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def get_site_config(self, site_name: str) -> Dict[str, Any]:
        """Get configuration for a specific site."""
        return self.config["sites"].get(site_name, {})

    def get_timeout(self, timeout_type: str) -> int:
        """Get timeout configuration."""
        return self.config["timeouts"].get(timeout_type, 30000)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
