import json
from email_poller import EmailPoller


def load_config(file_path="config.json"):
    """Loads the main configuration file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Please create it.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode {file_path}. Please check its format.")
        return None


def trigger_action(code):
    """
    This is the placeholder for your 'TriggerActions'.
    It's called when a code is successfully extracted.

    For now, it just prints the code and a sample URL.
    You could extend this to use a library like Selenium to
    automatically click buttons on a website.
    """
    print("\n--- ACTION TRIGGERED ---")
    print(f"Successfully extracted code: {code}")

    # Example of a trigger action:
    config = load_config()
    if config:
        target_url_template = config.get("trigger_actions", {}).get("target_url")
        if target_url_template:
            final_url = target_url_template.replace("{code}", code)
            print(f"Would navigate to: {final_url}")
    print("------------------------\n")


def main():
    """Main function to initialize and run the email poller."""
    config = load_config()
    if not config:
        return

    # The poller is initialized with the trigger_action function as a callback
    poller = EmailPoller(config, action_callback=trigger_action)
    poller.poll()


if __name__ == "__main__":
    main()
