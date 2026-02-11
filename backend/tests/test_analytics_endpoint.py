from sqlalchemy import select

from app.models.pageview import Pageview


def pageview_rows(session_factory) -> list[Pageview]:
    with session_factory() as session:
        return list(session.scalars(select(Pageview)))


def test_pageview_is_persisted_with_request_metadata(client_with_overrides):
    client, session_factory, _ = client_with_overrides

    response = client.post(
        "/v1/analytics/pageview",
        headers={
            "User-Agent": "pytest-agent",
            "X-Forwarded-For": "203.0.113.7, 10.0.0.1",
        },
        json={
            "path": "/pricing?variant=a",
            "title": "Pricing",
            "referrer": "https://google.com",
            "session_id": "session-123",
        },
    )

    assert response.status_code == 204
    rows = pageview_rows(session_factory)
    assert len(rows) == 1

    pageview = rows[0]
    assert pageview.path == "/pricing?variant=a"
    assert pageview.title == "Pricing"
    assert pageview.referrer == "https://google.com"
    assert pageview.session_id == "session-123"
    assert pageview.user_agent == "pytest-agent"
    assert pageview.ip_address == "203.0.113.7"


def test_pageview_without_forwarded_ip_falls_back_to_client_ip(client_with_overrides):
    client, session_factory, _ = client_with_overrides

    response = client.post(
        "/v1/analytics/pageview",
        headers={"User-Agent": "ua-only"},
        json={"path": "/"},
    )

    assert response.status_code == 204
    rows = pageview_rows(session_factory)
    assert len(rows) == 1
    assert rows[0].ip_address is not None
    assert rows[0].user_agent == "ua-only"


def test_invalid_pageview_payload_is_rejected(client_with_overrides):
    client, session_factory, _ = client_with_overrides

    response = client.post("/v1/analytics/pageview", json={"title": "Missing path"})

    assert response.status_code == 422
    assert len(pageview_rows(session_factory)) == 0


def test_pageview_prefers_forwarded_ip_over_real_ip(client_with_overrides):
    client, session_factory, _ = client_with_overrides

    response = client.post(
        "/v1/analytics/pageview",
        headers={
            "User-Agent": "proxy-agent",
            "X-Forwarded-For": "198.51.100.11, 10.0.0.3",
            "X-Real-IP": "192.0.2.7",
        },
        json={"path": "/proxy-check"},
    )

    assert response.status_code == 204
    rows = pageview_rows(session_factory)
    assert len(rows) == 1
    assert rows[0].ip_address == "198.51.100.11"


def test_pageview_uses_real_ip_when_forwarded_header_is_absent(client_with_overrides):
    client, session_factory, _ = client_with_overrides

    response = client.post(
        "/v1/analytics/pageview",
        headers={
            "User-Agent": "real-ip-agent",
            "X-Real-IP": "203.0.113.45",
        },
        json={"path": "/real-ip-check"},
    )

    assert response.status_code == 204
    rows = pageview_rows(session_factory)
    assert len(rows) == 1
    assert rows[0].ip_address == "203.0.113.45"
    assert rows[0].user_agent == "real-ip-agent"


def test_pageview_payload_is_normalized(client_with_overrides):
    client, session_factory, _ = client_with_overrides

    response = client.post(
        "/v1/analytics/pageview",
        headers={"User-Agent": "normalize-agent"},
        json={
            "path": "  /normalize  ",
            "title": "   ",
            "referrer": "   ",
            "session_id": "  session-x  ",
        },
    )

    assert response.status_code == 204
    rows = pageview_rows(session_factory)
    assert len(rows) == 1
    assert rows[0].path == "/normalize"
    assert rows[0].title is None
    assert rows[0].referrer is None
    assert rows[0].session_id == "session-x"


def test_blank_path_is_rejected(client_with_overrides):
    client, session_factory, _ = client_with_overrides

    response = client.post("/v1/analytics/pageview", json={"path": "   "})

    assert response.status_code == 422
    assert len(pageview_rows(session_factory)) == 0
