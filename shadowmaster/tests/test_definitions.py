# tests/test_definitions.py

"""
This file defines the test cases for the AI-driven automation framework.
Each test case includes a URL and a series of steps. Steps are defined
with natural language descriptions for the AI to interpret.
"""

TEST_CASES = {
    "das_oertliche": {
        "url": "https://www.dasoertliche.de/",
        "steps": [
            {
                "type": "ai_shadow",
                "description": "The button to accept all cookies. The text is likely 'Alle Akzeptieren' or similar.",
            },
            {
                "type": "standard",
                "selector": "#meinOeLogin",
                "description": "The main login button, labeled 'Anmelden'.",
            },
            {
                "type": "ai_shadow",
                "description": "The username or email input field inside the login popup form.",
                "value": "testuser@example.com",
            },
        ],
    },
    "gelbe_seiten": {
        "url": "https://www.gelbeseiten.de/",
        "steps": [
            {
                "type": "ai_shadow",
                "description": "The primary button to accept all cookies. The text is likely 'Alle Akzeptieren' or 'Zustimmen'.",
            }
        ],
    },
    "reddit": {
        "url": "https://www.reddit.com/",
        "steps": [
            {
                "type": "standard",
                "selector": "#login-button",
                "description": "The main login button on the top right of the homepage.",
            },
            {
                "type": "ai_shadow",
                "description": "The link inside the login popup to 'Sign Up' instead of logging in.",
            },
            {
                "type": "ai_shadow",
                "description": "The email address input field on the sign-up form.",
                "value": "reddit.test@example.com",
            },
        ],
    },
}
