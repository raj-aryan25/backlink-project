import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class EmailClient:
    """Handles all interactions with the email provider's API (e.g., Gmail)."""

    def __init__(self, config):
        """Initializes the client with API configuration."""
        self.config = config
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticates with the Gmail API using OAuth 2.0."""
        creds = None
        token_file = self.config["token_file"]
        credentials_file = self.config["credentials_file"]
        scopes = self.config["scopes"]

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}. Please re-authenticate.")
                    creds = None  # Force re-authentication

            if not creds:
                if not os.path.exists(credentials_file):
                    print(f"Error: Credentials file not found at '{credentials_file}'")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes
                )
                creds = flow.run_local_server(port=0)

            with open(token_file, "w") as token:
                token.write(creds.to_json())

        try:
            return build("gmail", "v1", credentials=creds)
        except HttpError as error:
            print(f"An error occurred building the service: {error}")
            return None

    def list_messages(self, query):
        """Lists messages matching a given query."""
        if not self.service:
            return []
        try:
            result = (
                self.service.users().messages().list(userId="me", q=query).execute()
            )
            return result.get("messages", [])
        except HttpError as error:
            print(f"An error occurred listing messages: {error}")
            return []

    def get_message(self, message_id):
        """Retrieves a single message by its ID."""
        if not self.service:
            return None
        try:
            return (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
        except HttpError as error:
            print(f"An error occurred getting message {message_id}: {error}")
            return None

    def mark_as_read(self, message_id):
        """Marks a message as read by removing the 'UNREAD' label."""
        if not self.service:
            return
        try:
            self.service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            print(f"Marked message {message_id} as read.")
        except HttpError as error:
            print(f"An error occurred marking message {message_id} as read: {error}")
