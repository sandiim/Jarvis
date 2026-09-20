from models.email_models import (
    AnalyzedEmail,
    Email,
    EmailAnalysis,
)
from models.inbox_model import InboxSummary


def make_email(
    email_id: str = "email-123",
    subject: str = "Technical Interview",
) -> Email:
    return Email(
        id=email_id,
        subject=subject,
        sender="recruiter@example.com",
        date="2026-09-20T10:00:00Z",
        body="Please confirm your availability for the interview.",
    )


def make_analysis() -> EmailAnalysis:
    return EmailAnalysis(
        summary="The recruiter requests interview availability.",
        category="recruitment",
        priority="high",
        action_required=True,
        action_items=["Confirm interview availability"],
    )


def make_analyzed_email(
    email_id: str = "email-123",
) -> AnalyzedEmail:
    return AnalyzedEmail(
        email=make_email(email_id=email_id),
        analysis=make_analysis(),
    )

def make_inbox_summary() -> InboxSummary:
    analyzed_email = make_analyzed_email()

    return InboxSummary(
        total_emails=1,
        high_priority=1,
        medium_priority=0,
        low_priority=0,
        action_required=1,
        categories={"recruitment": 1},
        emails=[analyzed_email],
    )