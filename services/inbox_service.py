from collections import Counter

from gmail.email_models import AnalyzedEmail , InboxSummary


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
