import logging

from sqlalchemy.orm import Session

from app.models.contact_submission import ContactSubmission
from app.schemas.contact import ContactSubmissionCreate
from app.services.slack import SlackNotifier

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(self, session: Session, slack_notifier: SlackNotifier):
        self.session = session
        self.slack_notifier = slack_notifier

    def create_submission(self, payload: ContactSubmissionCreate) -> ContactSubmission:
        submission = ContactSubmission(
            name=payload.name,
            email=payload.email,
            message=payload.message,
        )

        self.session.add(submission)
        self.session.commit()
        self.session.refresh(submission)

        try:
            self.slack_notifier.notify_contact_submission(submission)
        except Exception:
            logger.exception("Slack notification failed for contact_submission_id=%s", submission.id)

        return submission
