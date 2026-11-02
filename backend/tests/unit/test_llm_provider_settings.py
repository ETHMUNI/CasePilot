import pytest

from casepilot.exceptions.provider_configuration_error import (
    ProviderConfigurationError,
)
from casepilot.integrations.llm.provider_kind import LLMProviderKind
from casepilot.integrations.llm.provider_settings import get_llm_provider_settings


def test_llm_provider_defaults_to_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CASEPILOT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("CASEPILOT_LLM_MODEL", raising=False)
    monkeypatch.delenv("CASEPILOT_LLM_API_KEY", raising=False)

    settings = get_llm_provider_settings()

    assert settings.provider is LLMProviderKind.DISABLED
    assert settings.model is None


def test_openai_provider_requires_model_and_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CASEPILOT_LLM_PROVIDER", "openai")
    monkeypatch.setenv("CASEPILOT_LLM_MODEL", "test-model")
    monkeypatch.delenv("CASEPILOT_LLM_API_KEY", raising=False)

    with pytest.raises(ProviderConfigurationError, match="API_KEY is required"):
        get_llm_provider_settings()


def test_provider_settings_do_not_reveal_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CASEPILOT_LLM_PROVIDER", "openai")
    monkeypatch.setenv("CASEPILOT_LLM_MODEL", "test-model")
    monkeypatch.setenv("CASEPILOT_LLM_API_KEY", "secret-test-key")

    settings = get_llm_provider_settings()

    assert "secret-test-key" not in repr(settings)


@pytest.mark.parametrize("timeout", ["0", "-1", "nan", "inf"])
def test_llm_provider_requires_positive_finite_timeout(
    monkeypatch: pytest.MonkeyPatch, timeout: str
) -> None:
    monkeypatch.setenv("CASEPILOT_LLM_TIMEOUT_SECONDS", timeout)

    with pytest.raises(ProviderConfigurationError, match="positive number"):
        get_llm_provider_settings()
