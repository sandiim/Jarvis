from collections import Counter

from models.email_models import AnalyzedEmail
from models.inbox_model import InboxSummary
from gmail.email_service import get_email_by_id, get_latest_message_ids 
from ai.email_analyzer import analyze_emails , analyze_email



def build_inbox_summary(
    emails: list[AnalyzedEmail],
) -> InboxSummary:

    priorities = Counter(
        item.analysis.priority
        for item in emails
    )

    categories = Counter(
        item.analysis.category
        for item in emails
    )

    action_count = sum(
        1
        for item in emails
        if item.analysis.action_required
    )

    return InboxSummary(
        total_emails=len(emails),

        high_priority=priorities.get(
            "high",
            0,
        ),

        medium_priority=priorities.get(
            "medium",
            0,
        ),

        low_priority=priorities.get(
            "low",
            0,
        ),

        action_required=action_count,

        categories=dict(categories),
    )


PRIORITY_ORDER = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


def sort_by_priority(
    emails: list[AnalyzedEmail],
) -> list[AnalyzedEmail]:

    return sorted(
        emails,
        key=lambda item: PRIORITY_ORDER[
            item.analysis.priority
        ],
        reverse=True,
    )


def filter_by_category(
    emails: list[AnalyzedEmail],
    category: str,
) -> list[AnalyzedEmail]:

    return [
        item
        for item in emails
        if item.analysis.category == category
    ]


def analyze_latest_inbox(
    gmail_service,
    max_results: int = 5,
    query: str | None = None,
) -> InboxSummary:
    message_ids = get_latest_message_ids(
        gmail_service,
        max_results=max_results,
        query=query,
    )

    emails = [
        get_email_by_id(gmail_service, message_id)
        for message_id in message_ids
    ]

    analyzed_emails = analyze_emails(emails)
    return build_inbox_summary(analyzed_emails)