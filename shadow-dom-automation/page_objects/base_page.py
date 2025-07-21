from playwright.async_api import Page
from utils.shadow_dom_helper import find_element_in_shadow_dom


class BasePage:
    """
    The BasePage class serves as the foundation for all page objects.
    It holds a reference to the Playwright page object and provides
    a method for navigating to URLs.
    """

    def __init__(self, page: Page):
        """
        Initializes the BasePage with a Playwright page object.

        Args:
            page: The Playwright Page object.
        """
        self.page = page
        self.shadow_dom_helper = find_element_in_shadow_dom

    async def navigate(self, url: str):
        """
        Navigates to the specified URL.

        Args:
            url: The URL to navigate to.
        """
        await self.page.goto(url)
