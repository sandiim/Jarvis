from pydantic import BaseModel, Field


class Email(BaseModel):
    id: str
    subject: str
    sender: str
    date: str
    body: str


class EmailSummary(BaseModel):
    summary: str