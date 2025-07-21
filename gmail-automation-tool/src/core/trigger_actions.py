from playwright.async_api import Page
import asyncio
import logging


class TriggerActions:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)

    async def navigate_to_site(self, url: str):
        """Navigate to the target site"""
        await self.page.goto(url)
        await asyncio.sleep(2)

    async def trigger_email_verification(self, site_config: dict):
        """Trigger email verification based on site configuration"""
        trigger_config = site_config.get("email_trigger", {})
        selector = trigger_config.get("selector")

        if not selector:
            self.logger.error("No trigger selector configured")
            return False

        try:
            # Wait for element to be visible
            element = self.page.locator(selector).first
            await element.wait_for(state="visible", timeout=10000)

            # Click the trigger element
            await element.click()

            self.logger.info(
                f"Successfully triggered email verification using: {selector}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to trigger email verification: {e}")
            return False

    async def login_flow_hotfrog(self):
        """Specific login flow for Hotfrog"""
        try:
            # Fill username/email
            email_input = self.page.locator(
                "input[type='email'], input[name='email']"
            ).first
            await email_input.wait_for(state="visible", timeout=10000)
            await email_input.fill("test@example.com")

            # Fill password
            password_input = self.page.locator("input[type='password']").first
            await password_input.fill("testpassword123")

            # Click login button
            login_btn = self.page.locator(
                "button[type='submit'], input[type='submit']"
            ).first
            await login_btn.click()

            await asyncio.sleep(2)
            return True

        except Exception as e:
            self.logger.error(f"Hotfrog login flow failed: {e}")
            return False
