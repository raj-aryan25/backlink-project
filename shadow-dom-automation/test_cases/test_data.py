# test_cases/test_data.py

"""
This file centralizes all data and selectors for the test cases.
It follows a data-driven approach, separating the test data
from the execution logic.
"""

TEST_CASES = {
    "das_oertliche": {
        "url": "https://www.dasoertliche.de/",
        "steps": [
            {
                "description": "Accept Cookies",
                "js_path": "document.querySelector('#cmpwrapper').shadowRoot.querySelector('#cmpwelcomebtnyes > a')",
            },
            {
                "description": "Click Anmelden Button",
                "js_path": "document.querySelector('#meinOeLogin')",
            },
            {
                "description": "Enter Username",
                "js_path": "document.querySelector('#qlUsername')",
                "value": "testuser@example.com",
            },
        ],
    },
    "gelbe_seiten": {
        "url": "https://www.gelbeseiten.de/",
        "steps": [
            {
                "description": "Accept Cookies",
                "js_path": "document.querySelector('#cmpwrapper').shadowRoot.querySelector('#cmpwelcomebtnyes > a')",
            }
        ],
    },
    "reddit": {
        "url": "https://www.reddit.com/",
        "steps": [
            {
                "description": "Click Login Button",
                "js_path": "document.querySelector('#login-button')",
            },
            {
                "description": "Click Sign Up Link",
                "js_path": "document.querySelector('#login > auth-flow-modal > div.font-sans.bg-ui-modalbackground.pb-\\[env\\\\(safe-area-inset-bottom\\\\)\\] > div.lg\\\\:mt-sm.mt-md.text-14 > auth-flow-link')",
            },
            {
                "description": "Enter Email",
                "js_path": "document.querySelector('#register-email').shadowRoot.querySelector('label > div > span > span.input-container.activated > input[type=email]')",
                "value": "reddit.test@example.com",
            },
        ],
    },
}
