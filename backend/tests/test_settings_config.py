from app.core.config import get_settings


def test_database_url_prefers_explicit_database_url(monkeypatch):
    explicit_database_url = "postgresql+psycopg://explicit:secret@db-host:5432/explicit_db"
    monkeypatch.setenv("DATABASE_URL", explicit_database_url)
    monkeypatch.setenv("POSTGRES_DB", "ignored_db")
    monkeypatch.setenv("POSTGRES_USER", "ignored_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "ignored_password")
    monkeypatch.setenv("POSTGRES_HOST", "ignored-host")
    monkeypatch.setenv("POSTGRES_PORT", "6543")

    settings = get_settings()

    assert settings.database_url == explicit_database_url


def test_database_url_falls_back_to_postgres_parts(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_DB", "app_db")
    monkeypatch.setenv("POSTGRES_USER", "app_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret_pw")
    monkeypatch.setenv("POSTGRES_HOST", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "5432")

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://app_user:secret_pw@postgres:5432/app_db"
