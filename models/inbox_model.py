from pydantic import BaseModel, Field
from typing import Literal

class InboxSummary(BaseModel):
    total_emails: int

    high_priority: int
    medium_priority: int
    low_priority: int

    action_required: int

    categories: dict[str, int] = Field(
        default_factory=dict
    )