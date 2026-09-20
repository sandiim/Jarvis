import os.path
import base64
import re
import unicodedata
from html import unescape
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from models.email_models import Email, Attachment


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


def get_email_by_id(service, message_id: str) -> Email:
    message = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full",
        )
        .execute()
    )

    payload = message.get("payload", {})
    headers = payload.get("headers", [])

    subject = ""
    sender = ""
    date = ""

    for header in headers:
        name = header.get("name", "").lower()

        if name == "subject":
            subject = header.get("value", "")

        elif name == "from":
            sender = header.get("value", "")

        elif name == "date":
            date = header.get("value", "")

    raw_body = extract_email_body(payload)

    body = clean_email_body(raw_body)

    attachments = extract_attachments(payload)

    return Email(
        id=message_id,
        subject=subject,
        sender=sender,
        date=date,
        body=body,
        attachments=attachments,
    )

def decode_base64_data(data: str) -> str:
    if not data:
        return ""

    try:
        decoded_bytes = base64.urlsafe_b64decode(data)
        return decoded_bytes.decode("utf-8", errors="replace")
    except Exception:
        return ""



def html_to_text(html: str) -> str:
    if not html:
        return ""

    # Remove scripts/styles
    html = re.sub(
        r"<(script|style).*?>.*?</\1>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Add line breaks for common block tags
    html = re.sub(
        r"<br\s*/?>",
        "\n",
        html,
        flags=re.IGNORECASE,
    )

    html = re.sub(
        r"</(p|div|tr|li|h[1-6])>",
        "\n",
        html,
        flags=re.IGNORECASE,
    )

    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", "", html)

    text = unescape(text)

    # Clean excessive whitespace
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def extract_email_body(payload: dict) -> str:
    plain_texts = []
    html_texts = []

    def walk_parts(part: dict):
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data")

        if data:
            decoded = decode_base64_data(data).strip()

            if decoded:
                if mime_type == "text/plain":
                    plain_texts.append(decoded)

                elif mime_type == "text/html":
                    html_texts.append(html_to_text(decoded))

        for child in part.get("parts", []):
            walk_parts(child)

    walk_parts(payload)

    # Prefer useful plain text
    useful_plain = [
        text
        for text in plain_texts
        if len(text.strip()) > 20
        and not is_boilerplate(text)
    ]

    if useful_plain:
        return "\n\n".join(useful_plain).strip()

    # Fall back to HTML
    useful_html = [
        text
        for text in html_texts
        if len(text.strip()) > 20
    ]

    if useful_html:
        return "\n\n".join(useful_html).strip()

    return ""


def is_boilerplate(text: str) -> bool:
    normalized = text.lower()

    boilerplate_patterns = [
        "desinscription:",
        "désinscription:",
        "unsubscribe",
        "manage preferences",
        "email preferences",
    ]

    matches = sum(
        pattern in normalized
        for pattern in boilerplate_patterns
    )

    return matches > 0 and len(text) < 500


def extract_attachments(payload: dict) -> list[Attachment]:
    attachments = []

    def walk_parts(part: dict):
        filename = part.get("filename", "").strip()
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})

        if filename:
            attachments.append(
                Attachment(
                    filename=filename,
                    mime_type=mime_type,
                    attachment_id=body.get("attachmentId"),
                )
            )

        for child in part.get("parts", []):
            walk_parts(child)

    walk_parts(payload)

    return attachments

