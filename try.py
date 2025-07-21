from playwright.sync_api import sync_playwright, Playwright


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.gelbeseiten.de/")
    page.get_by_role("button", name="Alle Akzeptieren").click()
    page.wait_for_timeout(3000)
    # ---------------------
    context.close()
    browser.close()


# Use the synchronous context manager and call the regular function
with sync_playwright() as playwright:
    run(playwright)
