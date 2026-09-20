
from fastapi import APIRouter, Depends, HTTPException

from ai.email_analyzer import analyze_email, analyze_emails
from api.dependencies import provide_gmail_service
from gmail.email_service import (
    get_email_by_id,
    get_latest_message_ids
)
from models.api_models import InboxAnalysisRequest
from models.email_models import AnalyzedEmail
from models.inbox_model import InboxSummary
from services.inbox_service import analyze_latest_inbox

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


@router.post(
    "/emails/{message_id}",
    response_model=AnalyzedEmail,
)
def analyze_gmail_message(
    message_id: str,
    service=Depends(provide_gmail_service),
) -> AnalyzedEmail:
    try:
        email = get_email_by_id(service, message_id)
        return analyze_email(email)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to analyze Gmail message {message_id}.",
        ) from exc


@router.post("/inbox", response_model=InboxSummary)
def analyze_inbox(
    request: InboxAnalysisRequest,
    service=Depends(provide_gmail_service),
) -> InboxSummary:
    try:
        return analyze_latest_inbox(
            gmail_service=service,
            max_results=request.max_results,
            query=request.query,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to analyze the inbox.",
        ) from exc