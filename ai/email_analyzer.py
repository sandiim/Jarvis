import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from models.email_models import Email, EmailAnalysis, AnalyzedEmail
from ai.prompts import EMAIL_ANALYSIS_SYSTEM_PROMPT


load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="openai/gpt-oss-20b",
    temperature=0
)


structured_llm = llm.with_structured_output(EmailAnalysis)

def analyze_email(email: Email) -> EmailAnalysis:
    try:
        attachments = "None"

        if email.attachments:
            attachments = "\n".join(
                f"- {a.filename} ({a.mime_type})"
                for a in email.attachments
            )

        email_content = f"""
                Sender: {email.sender}
                Subject: {email.subject}
                Date: {email.date}

                Attachments:
                {attachments}

                Email body:
                {email.body}
                """

        return structured_llm.invoke(
            [
                (
                    "system",
                    EMAIL_ANALYSIS_SYSTEM_PROMPT,
                ),
                (
                    "human",
                    email_content,
                ),
            ]
        )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to analyze email {email.id}"
        ) from exc


def analyze_emails(
    emails: list[Email],
) -> list[AnalyzedEmail]:

    analyzed_emails = []

    for email in emails:
        analysis = analyze_email(email)

        analyzed_emails.append(
            AnalyzedEmail(
                email=email,
                analysis=analysis,
            )
        )

    return analyzed_emails



def get_action_required_emails(
    emails: list[AnalyzedEmail],
) -> list[AnalyzedEmail]:

    return [
        item
        for item in emails
        if item.analysis.action_required
    ]






