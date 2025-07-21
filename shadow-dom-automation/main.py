import asyncio
from playwright.async_api import async_playwright
from config import TARGET_URLS
from page_objects.site_handler import SiteHandler


async def main():
    """
    The main execution function for the automation framework.
    It launches a browser, iterates through the target URLs, and
    applies the automation logic to each site.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False
        )  # Set headless=True for background execution
        context = await browser.new_context()
        page = await context.new_page()

        for url in TARGET_URLS:
            print(f"\nProcessing {url}...")
            site_handler = SiteHandler(page)

            try:
                await site_handler.navigate(url)

                # 1. Handle the initial consent pop-up
                await site_handler.handle_shadow_popup()
                await asyncio.sleep(2)  # Wait a moment after handling popup

                # 2. Perform site-specific actions
                if "dasoertliche.de" in url or "reddit.com" in url:
                    await site_handler.perform_login_action()

                print(f"Successfully processed {url}")

            except Exception as e:
                print(f"An error occurred while processing {url}: {e}")

            await asyncio.sleep(3)  # Pause between sites

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
