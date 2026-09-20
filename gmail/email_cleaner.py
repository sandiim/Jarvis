from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import unicodedata

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