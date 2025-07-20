"""
Reddit Page Object for ShadowMaster Framework
Handles Reddit-specific interactions and elements.
"""

from pages.base_page import BasePage
from typing import Dict, Any
import logging
import asyncio

logger = logging.getLogger(__name__)


class RedditPage(BasePage):
    """Page object for Reddit authentication and interaction."""

    def __init__(self, page, config: Dict[str, Any]):
        super().__init__(page, config)
        self.login_modal_open = False

    def _get_critical_elements(self) -> list:
        """Critical elements that should be present on Reddit."""
        return [
            "body",
            "[data-testid='login-button'], text='Log In'",
            "header, nav"
        ]

    async def open_login_modal(self) -> bool:
        """
        Open the login modal on Reddit.

        Returns:
            True if modal opened successfully, False otherwise
        """
        try:
            # Look for login button in header
            login_selectors = [
                "[data-testid='login-button']",
                "text='Log In'",
                "text='LOG IN'",
                "a[href*='login']",
                "button:has-text('Log In')"
            ]

            for selector in login_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.click(selector)
                    logger.info(f"Clicked login button using selector: {selector}")

                    # Wait for modal to appear
                    await self.page.wait_for_selector(
                        "[data-testid='login-modal'], .modal, [role='dialog']",
                        timeout=5000
                    )

                    self.login_modal_open = True
                    return True

                except Exception:
                    continue

            logger.warning("Could not find or click login button")
            return False

        except Exception as e:
            logger.error(f"Error opening login modal: {e}")
            return False

    async def switch_to_signup(self) -> bool:
        """
        Switch from login to signup form.

        Returns:
            True if switched successfully, False otherwise
        """
        try:
            signup_selectors = [
                "text='Sign up'",
                "text='SIGN UP'",
                "[data-testid='signup-button']",
                "button:has-text('Sign up')",
                ".signup-tab, .register-tab"
            ]

            for selector in signup_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    await self.page.click(selector)
                    logger.info(f"Switched to signup using selector: {selector}")

                    # Wait for signup form to be visible
                    await asyncio.sleep(1)
                    return True

                except Exception:
                    continue

            logger.warning("Could not find signup option")
            return False

        except Exception as e:
            logger.error(f"Error switching to signup: {e}")
            return False

    async def fill_signup_email(self, email: str) -> bool:
        """
        Fill email field in signup form.

        Args:
            email: Email address to fill

        Returns:
            True if email filled successfully, False otherwise
        """
        email_selectors = [
            "input[name='email']",
            "input[type='email']",
            "[data-testid='email-input']",
            "input[placeholder*='email' i]",
            "#email"
        ]

        for selector in email_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                await self.page.fill(selector, email)
                logger.info(f"Filled email using selector: {selector}")
                return True

            except Exception:
                continue

        logger.error("Could not find or fill email field")
        return False

    async def fill_login_credentials(self, username: str, password: str) -> bool:
        """
        Fill login form with username and password.

        Args:
            username: Username or email
            password: Password

        Returns:
            True if credentials filled successfully, False otherwise
        """
        try:
            # Fill username
            username_filled = await self._fill_username_field(username)
            if not username_filled:
                return False

            # Fill password
            password_filled = await self._fill_password_field(password)
            if not password_filled:
                return False

            logger.info("Successfully filled login credentials")
            return True

        except Exception as e:
            logger.error(f"Error filling login credentials: {e}")
            return False

    async def _fill_username_field(self, username: str) -> bool:
        """Fill username field with fallback selectors."""
        username_selectors = [
            "input[name='username']",
            "input[name='email']",
            "[data-testid='username-input']",
            "input[placeholder*='username' i]",
            "input[placeholder*='email' i]",
            "#username"
        ]

        for selector in username_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                await self.page.fill(selector, username)
                logger.debug(f"Filled username using selector: {selector}")
                return True
            except Exception:
                continue

        return False

    async def _fill_password_field(self, password: str) -> bool:
        """Fill password field with fallback selectors."""
        password_selectors = [
            "input[name='password']",
            "input[type='password']",
            "[data-testid='password-input']",
            "input[placeholder*='password' i]",
            "#password"
        ]

        for selector in password_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                await self.page.fill(selector, password)
                logger.debug(f"Filled password using selector: {selector}")
                return True
            except Exception:
                continue

        return False

    async def submit_form(self) -> bool:
        """
        Submit the currently active form (login or signup).

        Returns:
            True if form submitted successfully, False otherwise
        """
        try:
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "[data-testid='submit-button']",
                "button:has-text('Log In')",
                "button:has-text('Sign up')",
                "button:has-text('Continue')"
            ]

            for selector in submit_selectors:
                try:
                    # Check if button is visible and enabled
                    element = self.page.locator(selector)
                    if await element.count() > 0:
                        if await element.is_visible() and await element.is_enabled():
                            await element.click()
                            logger.info(f"Submitted form using selector: {selector}")
                            return True
                except Exception:
                    continue

            # Try pressing Enter as fallback
            await self.page.keyboard.press("Enter")
            logger.info("Submitted form using Enter key")
            return True

        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return False

    async def handle_popups_and_overlays(self) -> bool:
        """
        Handle common Reddit popups and overlays.

        Returns:
            True if popups handled successfully, False otherwise
        """
        handled_any = False

        # Cookie consent
        cookie_selectors = [
            "button:has-text('Accept')",
            "button:has-text('I Accept')",
            "[data-testid='cookie-accept']",
            ".cookie-consent button"
        ]

        for selector in cookie_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    await self.page.click(selector, timeout=2000)
                    logger.info("Handled cookie consent")
                    handled_any = True
                    break
            except Exception:
                continue

        # App download prompt
        app_dismiss_selectors = [
            "button:has-text('Not now')",
            "button:has-text('Continue in browser')",
            "[data-testid='app-banner-dismiss']",
            ".app-banner .close"
        ]

        for selector in app_dismiss_selectors:
            try:
                if await self.page.locator(selector).count() > 0:
                    await self.page.click(selector, timeout=2000)
                    logger.info("Dismissed app download prompt")
                    handled_any = True
                    break
            except Exception:
                continue

        return handled_any

    async def search_subreddit(self, query: str) -> bool:
        """
        Search for a subreddit or post.

        Args:
            query: Search query

        Returns:
            True if search initiated successfully, False otherwise
        """
        try:
            search_selectors = [
                "input[placeholder*='Search' i]",
                "[data-testid='search-input']",
                "input[name='q']",
                "#search-input"
            ]

            for selector in search_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    await self.page.fill(selector, query)
                    await self.page.keyboard.press("Enter")
                    logger.info(f"Searched for: {query}")
                    return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return False

    async def close_modal(self) -> bool:
        """
        Close any open modal dialogs.

        Returns:
            True if modal closed successfully, False otherwise
        """
        try:
            close_selectors = [
                "button[aria-label='Close']",
                "[data-testid='close-button']",
                ".modal-close, .close-button",
                "button:has-text('×')",
                "[role='dialog'] button[aria-label*='close' i]"
            ]

            for selector in close_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector)
                        logger.info("Closed modal")
                        self.login_modal_open = False
                        return True
                except Exception:
                    continue

            # Try pressing Escape as fallback
            await self.page.keyboard.press("Escape")
            logger.info("Closed modal using Escape key")
            self.login_modal_open = False
            return True

        except Exception as e:
            logger.error(f"Error closing modal: {e}")
            return False
