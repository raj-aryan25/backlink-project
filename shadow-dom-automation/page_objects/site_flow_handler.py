# page_objects/site_flow_handler.py

from playwright.async_api import Page
from .base_page import BasePage
from utils.shadow_dom_helper import find_element_by_js_path
import logging
import re


class SiteFlowHandler(BasePage):
    """
    Handles the execution of a sequence of test steps for a given test case.
    It is responsible for locating elements, performing actions, and reporting results.
    """

    async def execute_test_flow(self, test_name: str, steps: list):
        """
        Executes a series of test steps from the test data.

        Args:
            test_name: The name of the current test case (e.g., "das_oertliche").
            steps: A list of step dictionaries, each defining an action.
        """
        for i, step in enumerate(steps):
            description = step["description"]
            logging.info(f"Executing step {i+1}: {description}")

            element = await find_element_by_js_path(self.page, step["js_path"])

            if element:
                # Sanitize description for filename
                safe_description = re.sub(r"[^a-zA-Z0-9_-]", "_", description)
                screenshot_path = (
                    f"results/screenshots/{test_name}_step_{i+1}_{safe_description}.png"
                )

                if "value" in step:
                    await element.fill(step["value"])
                else:
                    await element.click()

                await self.page.screenshot(path=screenshot_path)
                logging.info(
                    f"Step {i+1} successful. Screenshot saved to {screenshot_path}"
                )
            else:
                error_msg = f"Element not found for step: {description}"
                logging.error(error_msg)
                raise Exception(error_msg)
