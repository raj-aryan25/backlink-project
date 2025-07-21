from playwright.async_api import Page, Locator
from .base_page import BasePage
import asyncio


class SiteHandler(BasePage):
    """
    A "smart" page object that contains generalized logic to handle
    interactions across multiple target sites.
    """

    def __init__(self, page: Page):
        """
        Initializes the SiteHandler.

        Args:
            page: The Playwright Page object.
        """
        super().__init__(page)
        # Generic selectors that are likely to work across multiple sites
        self.popup_accept_selector = 'button:has-text("Accept all"), button:has-text("Agree"), button:has-text("Zustimmen")'
        self.email_input_selector = 'input[type="email"], input[name="email"]'
        self.login_button_selector = 'button:has-text("Login"), button:has-text("Sign In"), a:has-text("Anmelden")'

    async def handle_shadow_popup(self):
        """
        Finds and closes a cookie/consent pop-up that exists within a Shadow DOM.
        It uses a generic selector to identify the accept button.
        """
        print("Searching for shadow popup...")
        try:
            # Wait a bit for popups to appear
            await asyncio.sleep(3)
            accept_button = await self.shadow_dom_helper(
                self.page, self.popup_accept_selector
            )
            if accept_button:
                print("Popup found, attempting to click 'Accept' button.")
                # Since the helper returns a standard locator, we need to find the specific one
                # that is visible and enabled.
                all_buttons = self.page.locator(self.popup_accept_selector)
                count = await all_buttons.count()
                for i in range(count):
                    button = all_buttons.nth(i)
                    if await button.is_visible() and await button.is_enabled():
                        await button.click()
                        print("Popup handled successfully.")
                        return
            else:
                print("No shadow popup found with the generic selector.")
        except Exception as e:
            print(f"Could not handle popup: {e}")

    async def perform_login_action(self):
        """
        Performs a generic login action by finding a login button, clicking it,
        and then filling in an email address in a form that appears within a Shadow DOM.
        """
        print("Attempting to perform login action...")
        try:
            # 1. Find and click a generic login/signup button on the main page
            login_buttons = self.page.locator(self.login_button_selector)
            login_button_count = await login_buttons.count()
            if login_button_count > 0:
                for i in range(login_button_count):
                    button = login_buttons.nth(i)
                    if await button.is_visible():
                        await button.click()
                        print("Clicked main login/signup button.")
                        break

            # Wait for the login form to appear
            await asyncio.sleep(2)

            # 2. Find the email input field within a Shadow DOM
            email_input = await self.shadow_dom_helper(
                self.page, self.email_input_selector
            )

            if email_input:
                print("Email input found in Shadow DOM.")
                # Use the generic locator to fill the form
                all_inputs = self.page.locator(self.email_input_selector)
                count = await all_inputs.count()
                for i in range(count):
                    input_field = all_inputs.nth(i)
                    if (
                        await input_field.is_visible()
                        and await input_field.is_enabled()
                    ):
                        await input_field.fill("test@example.com")
                        print("Email input filled with 'test@example.com'.")
                        return
            else:
                print("Could not find email input in any Shadow DOM.")

        except Exception as e:
            print(f"An error occurred during login action: {e}")
