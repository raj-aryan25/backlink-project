# core/site_handler.py

from playwright.async_api import Page
from ai.ai_helper import AIHelper
from config import ACTION_DELAY
import logging
import re


class SiteHandler:
    """
    The main execution engine for the test framework. It processes test steps,
    using the AIHelper for dynamic element location.
    """

    def __init__(self, page: Page):
        self.page = page
        self.ai_helper = AIHelper()

    async def execute_flow(self, test_name: str, steps: list):
        """
        Executes a test flow, step by step.

        Args:
            test_name: The name of the test case.
            steps: The list of steps to execute.
        """
        for i, step in enumerate(steps):
            description = step["description"]
            logging.info(f"Executing step {i+1}: {description}")

            # Add a delay before each action for stability and to avoid bot detection.
            await self.page.wait_for_timeout(ACTION_DELAY)

            element = None
            try:
                if step["type"] == "standard":
                    selector = step["selector"]
                    logging.info(f"Using standard selector: {selector}")
                    element = self.page.locator(selector).first

                elif step["type"] == "ai_shadow":
                    html = await self.page.content()
                    logging.info("Querying AI for the best selector...")
                    selector = self.ai_helper.get_selector_from_html(html, description)
                    if not selector:
                        raise Exception("AI failed to provide a valid selector.")
                    element = self.page.locator(selector).first

                # Ensure the element is present before interacting
                await element.wait_for(state="visible", timeout=5000)

                # Perform the action
                if "value" in step:
                    await element.fill(step["value"])
                else:
                    await element.click()

                # Sanitize description for filename
                safe_description = re.sub(r"[^a-zA-Z0-9_-]", "_", description)
                screenshot_path = (
                    f"results/screenshots/{test_name}_step_{i+1}_{safe_description}.png"
                )
                await self.page.screenshot(path=screenshot_path)
                logging.info(f"Step successful. Screenshot saved to {screenshot_path}")

            except Exception as e:
                logging.error(f"Step {i+1} FAILED: {description}. Reason: {e}")
                raise  # Re-raise the exception to fail the test case
