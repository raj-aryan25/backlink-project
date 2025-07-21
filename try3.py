import os
import asyncio
import google.generativeai as genai
from playwright.async_api import async_playwright

# --- Configuration ---
# Set your Gemini API key as an environment variable
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
genai.configure(api_key="AIzaSyAmzNljHtrTjQtHSfm13NsUOHk1xeyRgeA")


async def main():
    """
    Main function to run the visual automation workflow.
    """
    # 1. DEFINE THE GEMINI PROMPT
    # This prompt instructs the model to act as a locator.
    prompt = """
    Look at this screenshot of a webpage.
    Identify the button for accepting all cookies.
    Return only the exact, case-sensitive text label of that button and nothing else.
    For example: 'Accept all', 'Alle Akzeptieren', 'Allow cookies'.
    """

    # 2. LAUNCH PLAYWRIGHT AND TAKE SCREENSHOT
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        try:
            # Navigate to a page that likely has a cookie banner
            await page.goto("https://www.dasoertliche.de/")
            await page.wait_for_load_state("networkidle")
            # Give the banner a moment to appear and take a screenshot
            # await page.wait_for_timeout(5000)  # Wait for the page to load
            print("📸 Taking a screenshot of the page...")
            screenshot_bytes = await page.screenshot()

            # 3. ANALYZE WITH GEMINI VISION
            print("📸 Screenshot taken. Asking Gemini to find the accept button...")
            model = genai.GenerativeModel("gemini-1.5-flash")

            response = await model.generate_content_async(
                [prompt, {"mime_type": "image/png", "data": screenshot_bytes}]
            )

            # Clean the response to get only the button text
            button_text = response.text.strip().replace("'", "").replace('"', "")

            if not button_text:
                print("❌ Gemini could not identify a button text.")
                return

            print(f"🧠 Gemini identified the button text as: '{button_text}'")

            # 4. CLICK THE BUTTON USING THE IDENTIFIED TEXT
            print(
                f"🤖 Playwright is now clicking the button with the label '{button_text}'..."
            )

            # Playwright finds the button by its role and accessible name (the text).
            # This works even if the button is in a shadow root.
            accept_button = page.get_by_role("button", name=button_text, exact=True)

            await accept_button.highlight()  # Highlight for visual confirmation
            await accept_button.click()

            print("✅ Button clicked successfully!")
            await page.wait_for_timeout(3000)  # Pause to observe result
            login_button_selector = "#meinOeLogin"
            login_button = page.locator(login_button_selector)
            await login_button.highlight()  # Highlight the login button
            await login_button.click()
            print("✅ Login button clicked successfully!")
            await page.wait_for_timeout(5000)
            # ...after clicking the main login button...
            print("✅ Login button clicked!")

            # --- NEW: HANDLE THE IFRAME AND FILL THE USERNAME FIELD ---
            print("🤖 The login form is in an iframe. Locating the frame first...")

            # This CSS selector finds the iframe with the name 'simple-login'.
            # You can find this by inspecting the page and looking for the <iframe> tag.
            frame = page.frame_locator(".nivo-lightbox-item")

            print("🤖 Finding the username field inside the iframe...")
            await frame.locator("body").wait_for()  # Wait for iframe to load

            # Define a new prompt for finding the username field
            username_prompt = """
            Look at this screenshot of a login form.
            Find the input field for the username or email address.
            Return only the exact placeholder text of that specific input field.
            For example: 'Benutzername', 'Email Address'.
            """

            print("📸 Taking screenshot of login form...")
            form_screenshot = await frame.locator("body").screenshot()

            print("🧠 Asking Gemini to find the username field's placeholder...")
            response = await model.generate_content_async(
                [username_prompt, {"mime_type": "image/png", "data": form_screenshot}]
            )
            placeholder_text = response.text.strip().replace("'", "").replace('"', "")

            if not placeholder_text:
                raise Exception("Gemini could not identify the placeholder text.")

            print(f"🤖 Gemini identified the placeholder as: '{placeholder_text}'")

            # Use the text from Gemini to locate the field and fill it
            username_field = frame.get_by_placeholder(placeholder_text, exact=True)

            await username_field.highlight()
            await username_field.fill("ai-driven-test@example.com")

            print("✅ Username entered successfully using AI-driven locator!")
            await page.wait_for_timeout(3000)

            # Now, use the 'frame' object to find the element.
            # username_field = frame.get_by_placeholder(
            #     "Benutzername", exact=True
            # )

            # await username_field.highlight()
            # await username_field.fill("test-user-123")

            # print("✅ Username entered successfully inside the iframe!")
            # print("✅ Email entered successfully!")
            # await page.wait_for_timeout(3000)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()


# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
