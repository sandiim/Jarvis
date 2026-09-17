import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from email_models import EmailSummary


load_dotenv()


llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="openai/gpt-oss-20b",
    temperature=0
)


structured_llm = llm.with_structured_output(EmailSummary)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are JARVIS, an email assistant.

        Analyze the provided email.

        Extract:
        - subject
        - sender
        - date

        Then produce a concise summary containing the important
        information, requests, deadlines, meetings, and actions required.

        Never invent information that is not present in the email.
        """
    ),
    (
        "human",
        """
        Email:

        {email_content}
        """
    )
])


email_chain = prompt | structured_llm


def analyze_email(email_content: str) -> EmailSummary:
    return email_chain.invoke({
        "email_content": email_content
    })