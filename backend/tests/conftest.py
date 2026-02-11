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


class StubSlackNotifier:
    def __init__(self):
        self.calls = []
        self.should_fail = False

    def notify_contact_submission(self, submission):
        self.calls.append(submission)
        if self.should_fail:
            raise RuntimeError("Slack delivery failed")


@pytest.fixture(autouse=True)
def clear_cached_runtime_state():
    get_settings.cache_clear()
    reset_rate_limiter_state()
    yield
    get_settings.cache_clear()
    reset_rate_limiter_state()


@pytest.fixture
def client_with_overrides():
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

    with TestClient(app) as test_client:
        yield test_client, testing_session_factory, notifier
