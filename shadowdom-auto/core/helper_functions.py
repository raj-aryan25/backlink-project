import asyncio
from playwright.async_api import async_playwright, Page, TimeoutError, Frame
from ai.gemini_wrapper import GeminiWrapper


async def handle_cookie_banner(page: Page, button_text: str):
    """Handles cookie banners by clicking the specified button."""
    try:
        if button_text and button_text != "None":
            print(f"   -> Accept found button: '{button_text}'")
            await page.get_by_role("button", name=button_text, exact=True).click(
                timeout=5000
            )
            print("   -> Cookie banner handled.")
            await page.wait_for_timeout(
                1000
            )  # Wait a moment for the banner to disappear
        else:
            print("   -> No cookie banner found.")
    except Exception as e:
        print(f"   -> Could not handle cookie banner: {e}")


async def click_login_signup_button(page: Page, button_text: str, signup: bool = False):
    """Clicks the main login button or link."""
    perform_action = "signup" if signup else "login"

    try:
        print(f"   -> {perform_action.capitalize()} button text: '{button_text}'")
        await page.get_by_text(button_text, exact=True).first.click(timeout=5000)
        print(f"   -> {perform_action.capitalize()} button clicked.")
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception as e:
        print(f"   -> Could not click {perform_action} button: {e}")


async def fill_input(page: Page, target_text: str, text_to_fill: str):
    """
    Uses Gemini to get the target text, then searches the main page and all
    child iframes to find and fill the corresponding input field.
    """
    try:
        print(
            f"   -> Gemini identified field text as: '{target_text}'. Searching all frames..."
        )
        # --- Combined Search Logic ---
        found_and_filled = False
        # Get a list of the main frame plus all of its direct child frames
        all_frames = [page.main_frame] + page.main_frame.child_frames

        for i, frame in enumerate(all_frames):
            # Create a prioritized list of locators to try for each frame
            locators_to_try = [
                ("placeholder", frame.get_by_placeholder(target_text, exact=True)),
                ("label", frame.get_by_label(target_text, exact=True)),
                ("role", frame.get_by_role("textbox", name=target_text)),
            ]

            for method, locator in locators_to_try:
                try:
                    await locator.fill(text_to_fill, timeout=2000)
                    print(
                        f"   -> ✅ Success! Found and filled via '{method}' in frame #{i}."
                    )
                    await locator.highlight()
                    found_and_filled = True
                    break  # Exit the inner loop (strategies)
                except TimeoutError:
                    continue  # Strategy failed, try the next one

            if found_and_filled:
                break  # Exit the outer loop (frames)
        if not found_and_filled:
            print(
                f"   -> ❌ ERROR: Could not find '{target_text}' in the main page or any direct iframe."
            )

    except Exception as e:
        print(f"   -> An error occurred while finding input: {e}")
