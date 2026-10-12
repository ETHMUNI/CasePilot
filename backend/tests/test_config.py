import pytest
from sqlalchemy.engine import URL

from casepilot.config import get_settings


def test_settings_read_environment_from_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CASEPILOT_ENV", "test")

    settings = get_settings()

    assert settings.environment == "test"


def test_settings_default_to_development(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CASEPILOT_ENV", raising=False)

    settings = get_settings()

    assert settings.environment == "development"


def test_settings_build_database_url_from_postgres_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POSTGRES_DB", "casepilot_test")
    monkeypatch.setenv("POSTGRES_USER", "casepilot user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p@ss:/word%")
    monkeypatch.setenv("POSTGRES_HOST", "127.0.0.1")
    monkeypatch.setenv("POSTGRES_PORT", "55432")

    settings = get_settings()

    assert isinstance(settings.database_url, URL)
    assert settings.database_url.drivername == "postgresql+psycopg"
    assert settings.database_url.username == "casepilot user"
    assert settings.database_url.password == "p@ss:/word%"
    assert settings.database_url.host == "127.0.0.1"
    assert settings.database_url.port == 55432
    assert settings.database_url.database == "casepilot_test"


def test_settings_require_database_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="POSTGRES_PASSWORD must be set"):
        get_settings()
