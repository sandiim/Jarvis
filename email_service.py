import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


def get_gmail_service():
    creds = None

    # Load previously saved credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # Authenticate if credentials don't exist or aren't valid
    if not creds or not creds.valid:

        # Refresh expired token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # First authentication
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save credentials for future executions
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service

def get_latest_message_ids(service, max_results=5):

    result = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results
        )
        .execute()
    )

    messages = result.get("messages", [])

    return [message["id"] for message in messages]