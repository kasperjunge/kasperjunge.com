from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.request_meta import extract_client_ip, extract_user_agent
from app.db.session import get_db_session
from app.schemas.analytics import PageviewCreate
from app.services.analytics_service import AnalyticsService
from app.services.rate_limit import RateLimitExceededError, enforce_rate_limit

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])


@router.post("/pageview", status_code=status.HTTP_204_NO_CONTENT)
def ingest_pageview(
    payload: PageviewCreate,
    request: Request,
    session: Session = Depends(get_db_session),
) -> Response:
    settings = get_settings()
    try:
        enforce_rate_limit(
            request=request,
            endpoint_name="analytics_pageview",
            limit_value=settings.rate_limit_analytics,
        )
    except RateLimitExceededError as error:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate_limit_exceeded") from error

    ip_address = extract_client_ip(request)
    user_agent = extract_user_agent(request)
    service = AnalyticsService(session=session)
    service.create_pageview(
        payload,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
