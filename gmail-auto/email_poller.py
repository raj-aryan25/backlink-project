import os.path
import json
import time
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def load_config():
    """Loads the configuration from config.json."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please create it.")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode config.json. Please check its format.")
        return None


def authenticate(config):
    """Handles user authentication for the Gmail API."""
    creds = None
    token_file = config["gmail_api"]["token_file"]
    credentials_file = config["gmail_api"]["credentials_file"]
    scopes = config["gmail_api"]["scopes"]

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Ensure credentials file exists
            if not os.path.exists(credentials_file):
                print(f"Error: Credentials file not found at '{credentials_file}'")
                print(
                    "Please download your credentials from Google Cloud Console and save it."
                )
                return None
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return creds


def poll_emails(service, config):
    """Polls the inbox for new emails that match the filter criteria."""
    print("Starting to poll emails...")
    start_time = time.time()

    while time.time() - start_time < config["poll_timeout_seconds"]:
        try:
            # Construct the query based on filters
            query_parts = ["is:unread"]
            if config["filters"].get("sender"):
                query_parts.append(f"from:{config['filters']['sender']}")
            if config["filters"].get("subject"):
                query_parts.append(f"subject:({config['filters']['subject']})")

            query = " ".join(query_parts)
            print(f"Searching with query: {query}")

            # List messages that match the query
            results = service.users().messages().list(userId="me", q=query).execute()
            messages = results.get("messages", [])

            if messages:
                print(f"Found {len(messages)} matching message(s).")
                for message_info in messages:
                    process_message(service, message_info["id"], config)
                return  # Exit after finding and processing messages
            else:
                print("No new matching messages found. Waiting...")
                time.sleep(config["poll_interval_seconds"])

        except HttpError as error:
            print(f"An error occurred: {error}")
            # If the error is due to insufficient permissions, guide the user.
            if error.resp.status == 403:
                print("Permission denied. This might be due to incorrect API scopes.")
                print(
                    f"The script requires the following scope(s): {config['gmail_api']['scopes']}"
                )
                print(
                    "Please delete your token.json file and re-run the script to authorize with the correct permissions."
                )
                return
            time.sleep(config["poll_interval_seconds"])

    print("Polling timed out.")


def process_message(service, message_id, config):
    """Fetches a single message and extracts information from it."""
    try:
        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )

        # Mark the email as read by removing the UNREAD label
        # This requires the 'https://www.googleapis.com/auth/gmail.modify' scope
        service.users().messages().modify(
            userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()

        payload = message.get("payload", {})
        body, mime_type = get_message_body(payload)

        if body:
            extract_information(body, mime_type, config)
        else:
            print(f"Could not find body for message ID: {message_id}")

    except HttpError as error:
        print(f"An error occurred while processing message {message_id}: {error}")


def get_message_body(payload):
    """
    Extracts the text body from the email payload.
    It prefers text/plain, but falls back to text/html.
    """
    plain_text_body = None
    html_body = None

    # Recurse through parts to find the best body
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    # Prefer plain text, so we can return immediately
                    return (
                        base64.urlsafe_b64decode(data.encode("UTF-8")).decode("utf-8"),
                        "text/plain",
                    )
            elif part.get("mimeType") == "text/html":
                data = part["body"].get("data")
                if data:
                    html_body = (
                        base64.urlsafe_b64decode(data.encode("UTF-8")).decode("utf-8"),
                        "text/html",
                    )
            # Recursive call for nested parts
            elif "parts" in part:
                nested_body, nested_mime = get_message_body(part)
                if nested_body and nested_mime == "text/plain":
                    return nested_body, nested_mime
                elif nested_body and not html_body:
                    html_body = nested_body, nested_mime

    # If we found an html body in the loop, return it
    if html_body:
        return html_body

    # If not a multipart message, check the body directly
    if "body" in payload:
        data = payload["body"].get("data")
        if data:
            mime_type = payload.get("mimeType", "text/plain")
            body = base64.urlsafe_b64decode(data.encode("UTF-8")).decode("utf-8")
            return body, mime_type

    return None, None


def extract_information(body, mime_type, config):
    """Uses regex to extract information from the email body."""

    text_to_search = body
    if mime_type == "text/html":
        # Simple regex to strip HTML tags for easier parsing
        text_to_search = re.sub(r"<[^>]+>", " ", body)

    regex = config["extraction"]["regex"]
    # Use re.DOTALL to make '.' match newlines, useful for multiline bodies
    match = re.search(regex, text_to_search, re.DOTALL)

    if match:
        # The first group in the match is the extracted code
        extracted_code = match.group(1)
        print(f"Successfully extracted code: {extracted_code}")
    else:
        print("Could not find a match for the extraction regex in the email body.")
        print("--- Start of Cleaned Email Body (first 500 chars) ---")
        print(text_to_search.strip()[:500])
        print("--- End of Cleaned Email Body ---")


def main():
    """Main function to drive the email polling and extraction process."""
    config = load_config()
    if not config:
        return

    creds = authenticate(config)
    if not creds:
        print("Could not authenticate. Exiting.")
        return

    service = build("gmail", "v1", credentials=creds)
    poll_emails(service, config)


if __name__ == "__main__":
    main()
