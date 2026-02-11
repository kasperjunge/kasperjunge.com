from sqlalchemy import desc, func, select

from app.models.contact_submission import ContactSubmission


def valid_payload() -> dict[str, str]:
    return {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "message": "I would love to collaborate on an AI project.",
        "website": "",
    }


def submission_count(session_factory) -> int:
    with session_factory() as session:
        return session.scalar(select(func.count(ContactSubmission.id)))


def latest_submission(session_factory) -> ContactSubmission | None:
    with session_factory() as session:
        statement = select(ContactSubmission).order_by(desc(ContactSubmission.id)).limit(1)
        return session.scalar(statement)


def test_contact_submission_is_persisted_and_notified(client_with_overrides):
    client, session_factory, notifier = client_with_overrides

    response = client.post("/v1/contact", json=valid_payload())

    assert response.status_code == 201
    payload = response.json()
    assert payload["ok"] is True
    assert payload["id"] is not None
    assert payload["created_at"] is not None
    assert submission_count(session_factory) == 1
    assert len(notifier.calls) == 1


def test_honeypot_submissions_return_success_without_persistence(client_with_overrides):
    client, session_factory, notifier = client_with_overrides
    payload = valid_payload()
    payload["website"] = "https://spam.example"

    response = client.post("/v1/contact", json=payload)

    assert response.status_code == 201
    assert response.json()["ok"] is True
    assert response.json()["id"] is None
    assert submission_count(session_factory) == 0
    assert len(notifier.calls) == 0


def test_slack_failures_do_not_break_contact_submission(client_with_overrides):
    client, session_factory, notifier = client_with_overrides
    notifier.should_fail = True

    response = client.post("/v1/contact", json=valid_payload())

    assert response.status_code == 201
    assert response.json()["ok"] is True
    assert submission_count(session_factory) == 1
    assert len(notifier.calls) == 1


def test_invalid_email_is_rejected(client_with_overrides):
    client, _, _ = client_with_overrides
    payload = valid_payload()
    payload["email"] = "not-an-email"

    response = client.post("/v1/contact", json=payload)

    assert response.status_code == 422


def test_contact_submission_normalizes_fields_before_persistence(client_with_overrides):
    client, session_factory, notifier = client_with_overrides
    payload = valid_payload()
    payload["name"] = "  Ada Lovelace  "
    payload["message"] = "  I would love to collaborate.  "
    payload["website"] = "   "

    response = client.post("/v1/contact", json=payload)

    assert response.status_code == 201
    submission = latest_submission(session_factory)
    assert submission is not None
    assert submission.name == "Ada Lovelace"
    assert submission.message == "I would love to collaborate."
    assert len(notifier.calls) == 1


def test_blank_required_contact_fields_are_rejected(client_with_overrides):
    client, session_factory, _ = client_with_overrides
    payload = valid_payload()
    payload["name"] = "   "
    payload["message"] = "   "

    response = client.post("/v1/contact", json=payload)

    assert response.status_code == 422
    assert submission_count(session_factory) == 0
