from pydantic import BaseModel, Field
from typing import Literal


class Attachment(BaseModel):
    filename: str
    mime_type: str
    attachment_id: str | None = None

class Email(BaseModel):
    id: str
    subject: str
    sender: str
    date: str
    body: str
    attachments: list[Attachment] = Field(default_factory=list)

class EmailAnalysis(BaseModel):
    summary: str = Field(
        description="A concise summary of the email content."
    )

    category: Literal[
        "recruitment",
        "education",
        "work",
        "finance",
        "security",
        "account",
        "newsletter",
        "personal",
        "promotion",
        "other",
    ]

    priority: Literal[
        "low",
        "medium",
        "high",
    ]

    action_required: bool

    action_items: list[str] = Field(
        default_factory=list,
        description="A list of specific action items or tasks that the user should take based on the email content."
    )


class AnalyzedEmail(BaseModel):
    email: Email
    analysis: EmailAnalysis
