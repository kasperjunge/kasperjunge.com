from app.core.config import get_settings
from app.services.slack import SlackNotifier


def get_slack_notifier() -> SlackNotifier:
    settings = get_settings()
    webhook_url = str(settings.slack_webhook_url) if settings.slack_webhook_url else None
    return SlackNotifier(webhook_url=webhook_url)
