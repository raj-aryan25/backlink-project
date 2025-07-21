import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import email
from typing import List, Dict
import logging


class EmailClient:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, credentials_file: str, token_file: str):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.logger = logging.getLogger(__name__)
        self.authenticate()

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_file, "wb") as token:
                pickle.dump(creds, token)

        self.service = build("gmail", "v1", credentials=creds)
        self.logger.info("Successfully authenticated with Gmail API")

    def get_recent_messages(self, query: str = "", max_results: int = 10) -> List[Dict]:
        """Fetch recent messages based on query"""
        try:
            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            detailed_messages = []

            for message in messages:
                msg_detail = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="full")
                    .execute()
                )
                detailed_messages.append(self._parse_message(msg_detail))

            return detailed_messages

        except Exception as e:
            self.logger.error(f"Failed to fetch messages: {e}")
            return []

    def _parse_message(self, message: Dict) -> Dict:
        """Parse Gmail message into structured format"""
        headers = {h["name"]: h["value"] for h in message["payload"].get("headers", [])}

        body = ""
        if "parts" in message["payload"]:
            for part in message["payload"]["parts"]:
                if part["mimeType"] == "text/plain" or part["mimeType"] == "text/html":
                    data = part["body"].get("data")
                    if data:
                        body += base64.urlsafe_b64decode(data).decode("utf-8")
        else:
            data = message["payload"]["body"].get("data")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8")

        return {
            "id": message["id"],
            "subject": headers.get("Subject", ""),
            "sender": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "body": body,
            "headers": headers,
        }
