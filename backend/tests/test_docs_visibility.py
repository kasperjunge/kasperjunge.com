from fastapi.testclient import TestClient

from app.main import create_app


def test_docs_are_available_in_development(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    app = create_app()

    with TestClient(app) as client:
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200
        assert client.get("/redoc").status_code == 200


def test_docs_are_disabled_in_staging(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    app = create_app()

    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404
        assert client.get("/redoc").status_code == 404


def test_docs_are_disabled_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    app = create_app()

    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404
        assert client.get("/redoc").status_code == 404
