from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_slack_notifier
from app.core.config import get_settings
from app.db.session import get_db_session
from app.schemas.contact import ContactSubmissionCreate, ContactSubmissionResponse
from app.services.contact_service import ContactService
from app.services.rate_limit import RateLimitExceededError, enforce_rate_limit
from app.services.slack import SlackNotifier

router = APIRouter(prefix="/v1/contact", tags=["contact"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ContactSubmissionResponse)
def create_contact_submission(
    request: Request,
    payload: ContactSubmissionCreate,
    session: Session = Depends(get_db_session),
    slack_notifier: SlackNotifier = Depends(get_slack_notifier),
) -> ContactSubmissionResponse:
    settings = get_settings()
    try:
        enforce_rate_limit(
            request=request,
            endpoint_name="contact_submission",
            limit_value=settings.rate_limit_contact,
        )
    except RateLimitExceededError as error:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate_limit_exceeded") from error

    if payload.website:
        return ContactSubmissionResponse(ok=True)

    service = ContactService(session=session, slack_notifier=slack_notifier)
    submission = service.create_submission(payload=payload)

    return ContactSubmissionResponse(
        ok=True,
        id=submission.id,
        created_at=submission.created_at,
    )
