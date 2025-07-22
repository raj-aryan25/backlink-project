import asyncio
from playwright.async_api import async_playwright, Page, expect, TimeoutError
from core.automation_engine import AutomationEngine


async def main():
    """
    Main function to launch the browser and start the search.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=250)
        automation_engine = AutomationEngine(browser)
        await automation_engine.run_tasks()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
