from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import provide_gmail_service
from gmail.email_service import (
    get_email_by_id,
    get_latest_message_ids,
)
from models.email_models import Email

router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)


@router.get("", response_model=list[Email])
def list_emails(
    max_results: int = Query(default=5, ge=1, le=50),
    service=Depends(provide_gmail_service),
) -> list[Email]:
    try:
        message_ids = get_latest_message_ids(
            service,
            max_results=max_results,
        )

        return [
            get_email_by_id(service, message_id)
            for message_id in message_ids
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve emails from Gmail.",
        ) from exc


@router.get("/{message_id}", response_model=Email)
def get_email(
    message_id: str,
    service=Depends(provide_gmail_service),
) -> Email:
    try:
        return get_email_by_id(service, message_id)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to retrieve Gmail message {message_id}.",
        ) from exc