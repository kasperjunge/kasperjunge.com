import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_slack_notifier
from app.core.config import get_settings
from app.db.session import get_db_session
from app.main import create_app
from app.models.base import Base
from app.models.contact_submission import ContactSubmission  # noqa: F401
from app.models.pageview import Pageview  # noqa: F401
from app.services.rate_limit import reset_rate_limiter_state
from tests.conftest import StubSlackNotifier


def valid_contact_payload() -> dict[str, str]:
    return {
        "name": "Rate Limit Tester",
        "email": "ratelimit@example.com",
        "message": "Please contact us.",
        "website": "",
    }


@pytest.fixture
def rate_limited_client(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("REDIS_URL", "")
    monkeypatch.setenv("RATE_LIMIT_CONTACT", "2/minute")
    monkeypatch.setenv("RATE_LIMIT_ANALYTICS", "2/minute")
    get_settings.cache_clear()
    reset_rate_limiter_state()

    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    notifier = StubSlackNotifier()
    app = create_app()

    def override_db_session():
        db = testing_session_factory()
        try:
            yield db
        finally:
            db.close()

    def override_slack_notifier():
        return notifier

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_slack_notifier] = override_slack_notifier

    with TestClient(app) as client:
        yield client

    get_settings.cache_clear()
    reset_rate_limiter_state()


def test_contact_rate_limiting_blocks_after_threshold(rate_limited_client):
    client = rate_limited_client

    headers = {"X-Forwarded-For": "198.51.100.123"}
    assert client.post("/v1/contact", json=valid_contact_payload(), headers=headers).status_code == 201
    assert client.post("/v1/contact", json=valid_contact_payload(), headers=headers).status_code == 201

    third = client.post("/v1/contact", json=valid_contact_payload(), headers=headers)
    assert third.status_code == 429
    assert third.json() == {"detail": "rate_limit_exceeded"}


def test_analytics_rate_limiting_blocks_after_threshold(rate_limited_client):
    client = rate_limited_client

    headers = {"X-Forwarded-For": "203.0.113.222"}
    assert client.post("/v1/analytics/pageview", json={"path": "/first"}, headers=headers).status_code == 204
    assert client.post("/v1/analytics/pageview", json={"path": "/second"}, headers=headers).status_code == 204

    third = client.post("/v1/analytics/pageview", json={"path": "/third"}, headers=headers)
    assert third.status_code == 429
    assert third.json() == {"detail": "rate_limit_exceeded"}
