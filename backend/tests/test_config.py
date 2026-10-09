import pytest

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
