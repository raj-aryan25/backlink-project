import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright
from src.utils.config import Config
from src.core.email_client import EmailClient
from src.core.email_poller import EmailPoller
from src.core.code_parser import CodeParser
from src.core.trigger_actions import TriggerActions
from src.ai.email_ai_parser import EmailAIParser


@pytest.mark.asyncio
async def test_email_automation_flow():
    config = Config()

    # Initialize components
    email_config = config.get("email_config", {})
    email_client = EmailClient(
        email_config["gmail_api"]["credentials_file"],
        email_config["gmail_api"]["token_file"],
    )

    code_parser = CodeParser(config.get("regex_patterns", {}))

    # Initialize AI parser if configured
    ai_parser = None
    if config.get("ai_config", {}).get("enabled", False):
        api_key = config.get("ai_config", {}).get("openai_api_key")
        if api_key:
            ai_parser = EmailAIParser(api_key)

    email_poller = EmailPoller(email_client, code_parser, ai_parser)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        trigger_actions = TriggerActions(page)

        sites = config.get("test_sites", {})

        for site_name, site_config in sites.items():
            print(f"\nTesting email automation for: {site_name}")

            try:
                # Navigate to site
                await trigger_actions.navigate_to_site(site_config["url"])

                # Define trigger function
                async def trigger_func():
                    if site_name == "hotfrog":
                        await trigger_actions.login_flow_hotfrog()
                    return await trigger_actions.trigger_email_verification(site_config)

                # Poll for code/URL with trigger
                polling_config = config.get("email_config", {}).get("polling", {})

                result = await email_poller.poll_with_trigger(
                    trigger_func,
                    site_config.get("sender_patterns", []),
                    site_config.get("subject_patterns", []),
                    site_config.get("extraction_type", "otp"),
                    polling_config.get("interval_seconds", 5),
                    polling_config.get("timeout_seconds", 60),
                )

                if result:
                    print(
                        f"✓ Successfully extracted {site_config.get('extraction_type', 'code')}: {result}"
                    )
                else:
                    print(
                        f"✗ Failed to extract {site_config.get('extraction_type', 'code')} for {site_name}"
                    )

            except Exception as e:
                print(f"✗ Error testing {site_name}: {e}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_email_automation_flow())
