# utils/shadow_dom_helper.py

from playwright.async_api import Page, ElementHandle
import asyncio


async def find_element_by_js_path(page: Page, js_path: str) -> ElementHandle | None:
    """
    Finds an element using a direct JavaScript path.

    This function executes the provided JavaScript expression which should
    return a single DOM element. It's particularly useful for precisely
    targeting elements within Shadow DOMs when the exact path is known.

    Args:
        page: The Playwright Page object.
        js_path: A string containing the JavaScript code to locate the element.

    Returns:
        A Playwright ElementHandle for the found element, or None if not found.
    """
    try:
        element_handle = await page.evaluate_handle(js_path)
        if await element_handle.as_element():
            return element_handle.as_element()
    except Exception:
        return None
    return None


async def find_element_in_shadow_dom(page: Page, selector: str) -> ElementHandle | None:
    """
    Recursively searches for an element within all Shadow DOMs on a page.

    This function executes a JavaScript snippet in the browser to traverse the DOM
    and its shadow roots to find an element matching the given CSS selector.

    Args:
        page: The Playwright Page object.
        selector: The CSS selector of the element to find.

    Returns:
        A Playwright ElementHandle for the found element, or None if not found.
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

    if element_handle and await element_handle.as_element():
        return element_handle.as_element()
    return None
