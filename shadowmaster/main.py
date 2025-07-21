# main.py

import asyncio
import logging
import os
from playwright.async_api import async_playwright
from tests.test_definitions import TEST_CASES
from core.site_handler import SiteHandler


def setup_environment():
    """Creates necessary directories for test results and configures logging."""
    for dir_name in ["logs", "screenshots", "traces"]:
        os.makedirs(f"results/{dir_name}", exist_ok=True)

    # Configure logging to be rich and informative
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler("results/logs/test_run.log"),
            logging.StreamHandler(),
        ],
    )


async def run_tests():
    """Main function to initialize and run all defined test cases."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False
        )  # Run in headed mode for debugging

        for test_name, test_data in TEST_CASES.items():
            logging.info(f"--- Starting Test Case: {test_name} ---")
            context = await browser.new_context()
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = await context.new_page()

            try:
                handler = SiteHandler(page)
                await page.goto(test_data["url"], wait_until="domcontentloaded")
                await handler.execute_flow(test_name, test_data["steps"])
                logging.info(f"--- Test Case: {test_name} COMPLETED SUCCESSFULLY ---")

            except Exception as e:
                logging.error(f"--- Test Case: {test_name} FAILED ---")
                failure_screenshot = f"results/screenshots/{test_name}_FAILURE.png"
                await page.screenshot(path=failure_screenshot)
                logging.info(f"Failure screenshot saved to {failure_screenshot}")

            finally:
                trace_path = f"results/traces/{test_name}_trace.zip"
                await context.tracing.stop(path=trace_path)
                logging.info(f"Playwright trace saved to {trace_path}")
                await context.close()

        await browser.close()


if __name__ == "__main__":
    setup_environment()
    asyncio.run(run_tests())
