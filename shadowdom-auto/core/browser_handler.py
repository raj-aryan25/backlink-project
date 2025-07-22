import asyncio
from playwright.async_api import async_playwright, Page, expect, TimeoutError
from core.helper_functions import (
    fill_input,
    handle_cookie_banner,
    click_login_signup_button,
)
from ai.gemini_wrapper import GeminiWrapper
from utils.prompts import (
    HANDLE_COOKIE_PROMPT,
    CLICK_LOGIN_PROMPT,
    CLICK_SIGNUP_PROMPT,
    FILL_EMAIL_PROMPT,
)


class BrowserHandler:
    def __init__(self):
        self.gemini = GeminiWrapper()

    async def accept_cookies(self, page: Page):
        """
        Accept cookies on the page if a button with 'Accept' text is found.
        """
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
            screenshot = await page.screenshot()
            response = await self.gemini.analyze_screenshot(
                screenshot, HANDLE_COOKIE_PROMPT
            )
            button_text = await self.gemini.get_button_text(response)
            await handle_cookie_banner(page, button_text)
        except Exception as e:
            print(f"Error handling cookies: {e}")

    async def click_sign_buttons(self, page: Page, signup: bool = False):
        """
        Click the login or signup button on the page.
        """
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
            screenshot = await page.screenshot()
            response = await self.gemini.analyze_screenshot(
                screenshot, CLICK_SIGNUP_PROMPT if signup else CLICK_LOGIN_PROMPT
            )
            button_text = await self.gemini.get_button_text(response)
            await click_login_signup_button(page, button_text, signup)
        except Exception as e:
            print(f"Error clicking { 'signup' if signup else 'login' } button: {e}")

    async def find_and_fill_input(
        self, page: Page, field_description: str, text_to_fill: str
    ):
        """
        Find and fill an input field based on its description.
        """
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
            screenshot = await page.screenshot()
            response = await self.gemini.analyze_screenshot(
                screenshot,
                FILL_EMAIL_PROMPT.format(field_description=field_description),
            )
            target_text = await self.gemini.get_button_text(response)
            await fill_input(page, target_text, text_to_fill)
        except Exception as e:
            print(f"Error filling input field '{field_description}': {e}")
