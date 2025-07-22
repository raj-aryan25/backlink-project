import time
from email_client import EmailClient
from code_parser import CodeParser


class EmailPoller:
    """Polls an email inbox, processes messages, and triggers actions."""

    def __init__(self, config, action_callback):
        """
        Initializes the poller.

        Args:
            config (dict): The application configuration.
            action_callback (function): The function to call with the extracted code.
        """
        self.config = config.get("email_poller", {})
        self.client = EmailClient(config.get("email_client", {}))
        self.parser = CodeParser(config.get("code_parser", {}))
        self.action_callback = action_callback

    def poll(self):
        """Starts the polling loop to check for new emails."""
        if not self.client.service:
            print("Email client failed to initialize. Aborting poll.")
            return

        print("Starting to poll emails...")
        start_time = time.time()
        timeout = self.config.get("poll_timeout_seconds", 60)

        while time.time() - start_time < timeout:
            # Construct the search query
            filters = self.config.get("filters", {})
            query_parts = ["is:unread"]
            if filters.get("sender"):
                query_parts.append(f"from:{filters['sender']}")
            if filters.get("subject"):
                query_parts.append(f"subject:({filters['subject']})")
            query = " ".join(query_parts)

            print(f"Searching with query: {query}")
            messages = self.client.list_messages(query)

            if messages:
                print(f"Found {len(messages)} matching message(s).")
                for msg_info in messages:
                    message_id = msg_info["id"]
                    full_message = self.client.get_message(message_id)
                    if full_message:
                        self._process_message(full_message)
                        self.client.mark_as_read(message_id)
                return  # Exit after finding and processing messages
            else:
                print("No new matching messages found. Waiting...")
                time.sleep(self.config.get("poll_interval_seconds", 5))

        print("Polling timed out.")

    def _process_message(self, message):
        """Processes a single email message."""
        payload = message.get("payload", {})
        body, mime_type = self.parser.get_body(payload)

        if body:
            extracted_code = self.parser.extract_code(body, mime_type)
            if extracted_code:
                self.action_callback(extracted_code)
        else:
            print(f"Could not find body for message ID: {message.get('id')}")
