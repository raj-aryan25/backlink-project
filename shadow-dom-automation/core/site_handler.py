from playwright.async_api import Page
from ai.ai_helper import AIHelper
from config import ACTION_DELAY, GLOBAL_TIMEOUT
import logging


class SiteHandler:
    def __init__(self, page: Page):
        self.page = page
        self.ai_helper = AIHelper()

    async def execute_flow(self, test_name: str, steps: list):
        for i, step in enumerate(steps):
            description = step["description"]
            step_type = step["type"]
            logging.info(f"Executing step {i+1} ({step_type}): {description}")
            await self.page.wait_for_timeout(ACTION_DELAY)

            try:
                target_context = self.page
                host_locator = (
                    None  # To store the locator of the host element for waiting
                )

                # --- 1. Determine Context and Get Selector ---
                if step_type == "css":
                    selector = step["selector"]
                    logging.info(f"Using hardcoded CSS selector: {selector}")

                else:  # AI-driven types
                    if step_type == "iframe_ai":
                        iframe_locator = self.page.locator(step["iframe_selector"])
                        await iframe_locator.wait_for(state="visible", timeout=15000)
                        target_context = await iframe_locator.content_frame()
                        html_content = await target_context.content()

                    elif step_type == "ai_shadow":
                        host_locator = self.page.locator(step["shadow_host"])
                        # await host_locator.wait_for(state="visible", timeout=15000)
                        # --- NEW SMARTER WAIT LOGIC ---
                        # 1. First, wait for the element to be ATTACHED to the DOM.
                        #    This confirms it exists, even if it's not visible yet.
                        logging.info(
                            f"Waiting for shadow host '{step['shadow_host']}' to be attached..."
                        )
                        await host_locator.wait_for(
                            state="attached", timeout=GLOBAL_TIMEOUT
                        )

                        # 2. THEN, wait for it to become VISIBLE.
                        logging.info(
                            f"Waiting for shadow host '{step['shadow_host']}' to be visible..."
                        )
                        await host_locator.wait_for(
                            state="visible", timeout=GLOBAL_TIMEOUT
                        )
                        # --- END OF NEW LOGIC ---
                        html_content = await host_locator.evaluate(
                            "host => host.shadowRoot.innerHTML"
                        )

                    logging.info("Querying AI with specific HTML content...")
                    selector = self.ai_helper.get_selector_from_html(
                        html_content, description
                    )
                    if not selector:
                        raise Exception("AI failed to provide a selector.")
                    logging.info(f"AI provided selector: {selector}")

                # --- 2. Locate Element and Perform Action ---
                element = target_context.locator(selector).first
                await element.wait_for(state="visible", timeout=10000)

                if "value" in step:
                    await element.fill(step["value"])
                else:
                    await element.click()

                logging.info(
                    f"Action '{'fill' if 'value' in step else 'click'}' performed successfully."
                )

                # --- 3. CRITICAL: Synchronize After Action ---
                if step.get("wait_for_hidden") and host_locator:
                    logging.info(
                        f"Waiting for element '{step['shadow_host']}' to disappear..."
                    )
                    await host_locator.wait_for(state="hidden", timeout=10000)
                    logging.info("Element has disappeared as expected.")

                screenshot_path = (
                    f"results/screenshots/{test_name}_step_{i+1}_success.png"
                )
                await self.page.screenshot(path=screenshot_path)
                logging.info(f"Step successful. Screenshot saved to {screenshot_path}")

            except Exception as e:
                logging.error(f"Step {i+1} FAILED: {description}. Reason: {e}")
                raise
