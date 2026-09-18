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
from gmail.email_models import Email , Attachment

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

INVISIBLE_CODEPOINTS = {
    "\u034f",  # Combining Grapheme Joiner
    "\u200b",  # Zero Width Space
    "\u200c",  # Zero Width Non-Joiner
    "\u200d",  # Zero Width Joiner
    "\u2060",  # Word Joiner
    "\ufeff",  # Zero Width No-Break Space / BOM
}


def remove_invisible_characters(text: str) -> str:
    cleaned = []

    for char in text:
        if char in INVISIBLE_CODEPOINTS:
            continue

        category = unicodedata.category(char)

        if category in {"Cf", "Cc"} and char not in "\n\t":
            continue

        cleaned.append(char)

    return "".join(cleaned)

def normalize_whitespace(text: str) -> str:
    # Convert tabs to spaces
    text = text.replace("\t", " ")

    # Multiple spaces → single space
    text = re.sub(r"[ ]{2,}", " ", text)

    # Remove spaces before newline
    text = re.sub(r" +\n", "\n", text)

    # Maximum 2 consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


NOISE_LINES = {
    "follow",
    "complete profile",
    "view job",
    "view all jobs",
    "manage profile",
}


def remove_noise_lines(text: str) -> str:
    result = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.lower() in NOISE_LINES:
            continue

        # Standalone bullets add no information
        if stripped in {"•", "·"}:
            continue

        result.append(line)

    return "\n".join(result)


def remove_separator_lines(text: str) -> str:
    lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped in {"-", "--"}:
            continue

        lines.append(line)

    return "\n".join(lines)


UUID_LINK_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}"
    r"\s*\(\[link\]\)\s*$"
)


def remove_tracking_lines(text: str) -> str:
    lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if UUID_LINK_PATTERN.match(stripped):
            continue

        lines.append(line)

    return "\n".join(lines)


NOISE_PATTERNS = [
    re.compile(r".*preview line\s*-->\s*$", re.IGNORECASE),
]


def remove_noise_patterns(text: str) -> str:
    result = []

    for line in text.splitlines():
        if any(pattern.match(line.strip()) for pattern in NOISE_PATTERNS):
            continue

        result.append(line)

    return "\n".join(result)


FOOTER_MARKERS = {
    "privacy policy",
    "unsubscribe",
}


def trim_footer(text: str) -> str:
    lines = text.splitlines()

    if len(lines) < 10:
        return text

    cutoff_start = int(len(lines) * 0.6)

    for index in range(cutoff_start, len(lines)):
        normalized = lines[index].strip().lower()

        if normalized in {
            "unsubscribe",
            "privacy policy",
        }:
            return "\n".join(lines[:index]).strip()

    return text


def normalize_punctuation_spacing(text: str) -> str:
    text = re.sub(r"\[\s*link\s*\]", "[link]", text)

    # Remove spaces before closing punctuation
    text = re.sub(r"\s+([),.;:!?])", r"\1", text)

    # Remove spaces after opening parenthesis
    text = re.sub(r"\(\s+", "(", text)

    return text


def normalize_lines(text: str) -> str:
    cleaned_lines = []

    for line in text.splitlines():
        # Convert odd spaces to normal spaces
        line = line.replace("\xa0", " ")

        # Strip indentation around each line
        line = line.strip()

        # Collapse repeated spaces inside the line
        line = re.sub(r"[ \t]{2,}", " ", line)

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Never allow more than one empty line
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def shorten_long_urls(text: str) -> str:
    url_pattern = re.compile(
        r"https?://[^\s)>]+"
    )

    def replace_url(match):
        url = match.group(0)

        if len(url) > 120:
            return "[link]"

        return url

    return url_pattern.sub(replace_url, text)


TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
    "dc_euid",
}


def clean_url(url: str) -> str:
    try:
        parsed = urlparse(url)

        params = parse_qsl(
            parsed.query,
            keep_blank_values=True,
        )

        cleaned_params = [
            (key, value)
            for key, value in params
            if key.lower() not in TRACKING_PARAMS
        ]

        cleaned_query = urlencode(cleaned_params)

        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                cleaned_query,
                "",
            )
        )

    except Exception:
        return url

def clean_urls(text: str) -> str:
    url_pattern = re.compile(
        r"https?://[^\s)>]+"
    )

    def replace(match):
        url = match.group(0)

        cleaned = clean_url(url)

        if len(cleaned) > 120:
            return "[link]"

        return cleaned

    return url_pattern.sub(replace, text)


def clean_email_body(text: str) -> str:
    if not text:
        return ""

    text = remove_invisible_characters(text)

    text = clean_urls(text)

    text = normalize_punctuation_spacing(text)

    text = normalize_lines(text)

    text = remove_tracking_lines(text)

    text = remove_noise_lines(text)

    text = remove_noise_patterns(text)

    text = remove_separator_lines(text)

    text = trim_footer(text)

    # Final normalization because previous stages
    # may have introduced extra blank lines
    text = normalize_lines(text)

    return text.strip()