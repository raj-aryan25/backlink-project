from core.browser_handler import BrowserHandler
from utils.task_loader import task_loader
from playwright.async_api import Page, Browser, TimeoutError


class AutomationEngine:
    def __init__(self, browser: Browser):
        self.browser_handler = BrowserHandler()
        self.task_loader = task_loader("tasks/tasks.json")
        self.steps = self.task_loader.get_steps()
        self.browser = browser

    async def run_tasks(self):
        """
        Run the tasks defined in the task file on the given page.
        """
        for step in self.steps:
            url = step["url"]
            actions = step["actions"]
            details = step["details"]
            context = await self.browser.new_context()
            page = await context.new_page()
            try:
                await page.goto(url)

                for action in actions:
                    if action == "accept_cookies":
                        await self.browser_handler.accept_cookies(page)
                    elif action == "click_login_button":
                        await self.browser_handler.click_sign_buttons(
                            page, signup=False
                        )
                    elif action == "click_signup_button":
                        await self.browser_handler.click_sign_buttons(page, signup=True)
                    elif "fill_login_details" in action:
                        await self.browser_handler.find_and_fill_input(
                            page, "login", details.get("login", "")
                        )
                    elif "fill_signup_details" in action:
                        await self.browser_handler.find_and_fill_input(
                            page, "email", details.get("email", "")
                        )
            except Exception as e:
                print(f"Error occurred while processing actions for {url}: {e}")
            finally:
                await context.close()
