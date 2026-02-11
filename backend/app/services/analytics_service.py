from sqlalchemy.orm import Session

from app.models.pageview import Pageview
from app.schemas.analytics import PageviewCreate


class AnalyticsService:
    def __init__(self, session: Session):
        self.session = session

    def create_pageview(
        self,
        payload: PageviewCreate,
        *,
        user_agent: str | None,
        ip_address: str | None,
    ) -> Pageview:
        pageview = Pageview(
            path=payload.path,
            title=payload.title,
            referrer=payload.referrer,
            session_id=payload.session_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self.session.add(pageview)
        self.session.commit()
        self.session.refresh(pageview)
        return pageview
