import logging
from time import sleep

import httpx

from app.models.contact_submission import ContactSubmission

logger = logging.getLogger(__name__)


class SlackNotifier:
    def __init__(self, webhook_url: str | None, timeout_seconds: float = 5.0, max_attempts: int = 2):
        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts

    def notify_contact_submission(self, submission: ContactSubmission) -> None:
        if not self.webhook_url:
            logger.warning("SLACK_WEBHOOK_URL is not configured; skipping Slack notification.")
            return

        payload = {
            "text": "New contact form submission",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*New contact form submission*",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Name:*\n{submission.name}"},
                        {"type": "mrkdwn", "text": f"*Email:*\n{submission.email}"},
                    ],
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Message:*\n{submission.message}"},
                },
            ],
        }

        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(self.webhook_url, json=payload)
                    response.raise_for_status()
                return
            except Exception as error:
                last_error = error
                if attempt < self.max_attempts:
                    sleep(0.2 * attempt)

        if last_error:
            raise RuntimeError("Failed to send Slack notification.") from last_error
