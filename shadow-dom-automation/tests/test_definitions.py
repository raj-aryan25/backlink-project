# This file defines the test cases using a hybrid approach.
# 'type': 'css' for standard, reliable selectors.
# 'type': 'ai_shadow' for complex elements requiring AI analysis.
# 'description' for AI is now more detailed, guiding it to look for specific attributes.
# 'wait_for_hidden': A new key to specify a selector that should disappear after an action.
TEST_CASES = {
    "das_oertliche": {
        "url": "https://www.dasoertliche.de/",
        "steps": [
            {
                "type": "ai_shadow",
                "description": "The main button to accept cookies. Look for text like 'Alle Akzeptieren' inside a button or link. Check aria-labels and roles.",
                "shadow_host": "#cmpwrapper",
                "wait_for_hidden": True,  # After clicking, wait for the host to disappear
            },
            {
                "type": "css",
                "selector": "button#meinOeLogin",  # Per assignment, use a direct selector
                "description": "The 'Anmelden' (login) button.",
            },
            {
                "type": "ai_shadow",
                "description": "The input field for the username, likely labeled 'Benutzername'.",
                "shadow_host": "div[role='dialog']",  # A more generic selector for the modal
            },
        ],
    },
    "gelbe_seiten": {
        "url": "https://www.gelbeseiten.de/",
        "steps": [
            {
                "type": "ai_shadow",
                "description": "The primary button to accept all cookies. The text is likely 'Alle Akzeptieren'. Check button roles and aria-labels.",
                "shadow_host": "#cmpwrapper",
                "wait_for_hidden": True,
            }
        ],
    },
    "reddit": {
        "url": "https://www.reddit.com/",
        "steps": [
            {
                "type": "css",
                # This selector is much more stable as it targets the button by its slot and text content.
                "selector": "button[slot='login-button']",
                "description": "The main login button in the header.",
            },
            {
                "type": "iframe_ai",  # New type for AI interaction within an iframe
                "iframe_selector": "iframe[src^='https://www.reddit.com/login']",
                "description": "A link or button with the text 'Sign Up' to switch from the login to the registration form.",
            },
            {
                "type": "iframe_ai",
                "iframe_selector": "iframe[src^='https://www.reddit.com/login']",
                "description": "The input field for an email address on the sign-up form.",
                "value": "reddit.test.user@example.com",
            },
        ],
    },
}
