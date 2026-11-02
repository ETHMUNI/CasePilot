import math
import os
from dataclasses import dataclass, field

from pydantic import SecretStr

from casepilot.exceptions.provider_configuration_error import (
    ProviderConfigurationError,
)
from casepilot.integrations.llm.provider_kind import LLMProviderKind


@dataclass(frozen=True)
class LLMProviderSettings:
    provider: LLMProviderKind
    model: str | None
    api_key: SecretStr | None = field(repr=False)
    base_url: str | None
    timeout_seconds: float


def get_llm_provider_settings() -> LLMProviderSettings:
    provider_value = os.environ.get("CASEPILOT_LLM_PROVIDER", "disabled").lower()
    try:
        provider = LLMProviderKind(provider_value)
    except ValueError as error:
        raise ProviderConfigurationError(
            "CASEPILOT_LLM_PROVIDER must be disabled, openai, or ollama."
        ) from error

    model_value = os.environ.get("CASEPILOT_LLM_MODEL", "").strip()
    model = model_value or None
    api_key_value = os.environ.get("CASEPILOT_LLM_API_KEY") or None
    base_url = os.environ.get("CASEPILOT_LLM_BASE_URL") or None
    timeout_value = os.environ.get("CASEPILOT_LLM_TIMEOUT_SECONDS", "15")

    try:
        timeout_seconds = float(timeout_value)
    except ValueError as error:
        raise ProviderConfigurationError(
            "CASEPILOT_LLM_TIMEOUT_SECONDS must be a positive number."
        ) from error
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ProviderConfigurationError(
            "CASEPILOT_LLM_TIMEOUT_SECONDS must be a positive number."
        )

    if provider is not LLMProviderKind.DISABLED and not model:
        raise ProviderConfigurationError(
            "CASEPILOT_LLM_MODEL is required when an LLM provider is enabled."
        )
    if provider is LLMProviderKind.OPENAI and not api_key_value:
        raise ProviderConfigurationError(
            "CASEPILOT_LLM_API_KEY is required for the OpenAI provider."
        )

    return LLMProviderSettings(
        provider=provider,
        model=model,
        api_key=SecretStr(api_key_value) if api_key_value else None,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )
