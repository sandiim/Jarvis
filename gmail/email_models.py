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
    summary: str

    category: Literal[
        "work",
        "recruitment",
        "education",
        "finance",
        "newsletter",
        "personal",
        "account",
        "other",
    ]

    priority: Literal[
        "low",
        "medium",
        "high",
    ]

    action_required: bool

    action_items: list[str] = Field(
        default_factory=list
    )