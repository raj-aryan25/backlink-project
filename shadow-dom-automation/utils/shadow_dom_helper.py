import asyncio
from playwright.async_api import Page, Locator


async def find_element_in_shadow_dom(page: Page, selector: str) -> Locator | None:
    """
    Recursively searches for an element within all Shadow DOMs on a page.

    This function executes a JavaScript snippet in the browser to traverse the DOM
    and its shadow roots to find an element matching the given selector.

    Args:
        page: The Playwright Page object.
        selector: The CSS selector of the element to find.

    Returns:
        A Playwright Locator for the found element, or None if not found.
    """
    script = """
    (selector) => {
        const find = (root, selector) => {
            // 1. Search in the current root.
            const element = root.querySelector(selector);
            if (element) return element;

            // 2. Recursively search in all shadow roots within the current root.
            const allElements = root.querySelectorAll('*');
            for (const el of allElements) {
                if (el.shadowRoot) {
                    const foundInShadow = find(el.shadowRoot, selector);
                    if (foundInShadow) return foundInShadow;
                }
            }
            return null;
        };
        // 3. Start the search from the main document.
        return find(document, selector);
    }
    """
    element_handle = await page.evaluate_handle(script, selector)

    if await element_handle.get_property(
        "tagName"
    ):  # Check if a valid element was returned
        return page.locator(f"css={selector}")
    return None
