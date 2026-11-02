from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from casepilot.integrations.llm.provider_factory import build_analysis_provider
from casepilot.integrations.llm.provider_kind import LLMProviderKind
from casepilot.integrations.llm.provider_settings import LLMProviderSettings
from casepilot.services.analysis_provider import AnalysisProvider


def test_provider_factory_returns_none_when_disabled() -> None:
    settings = LLMProviderSettings(
        provider=LLMProviderKind.DISABLED,
        model=None,
        api_key=None,
        base_url=None,
        timeout_seconds=4.0,
    )

    assert build_analysis_provider(settings) is None


def test_provider_factory_configures_openai_timeout_without_retries() -> None:
    settings = LLMProviderSettings(
        provider=LLMProviderKind.OPENAI,
        model="test-model",
        api_key=SecretStr("test-key"),
        base_url="https://example.invalid/v1",
        timeout_seconds=4.0,
    )
    adapter = Mock(spec=AnalysisProvider)
    with (
        patch("langchain_openai.ChatOpenAI") as chat_openai,
        patch(
            "casepilot.integrations.llm.provider_factory.LangChainAnalysisProvider",
            return_value=adapter,
        ) as langchain_adapter,
    ):
        result = build_analysis_provider(settings)

    chat_openai.assert_called_once_with(
        model="test-model",
        api_key=settings.api_key,
        base_url="https://example.invalid/v1",
        timeout=4.0,
        max_retries=0,
        temperature=0,
    )
    langchain_adapter.assert_called_once_with(chat_openai.return_value)
    assert result is adapter


def test_provider_factory_configures_ollama_http_timeout() -> None:
    settings = LLMProviderSettings(
        provider=LLMProviderKind.OLLAMA,
        model="test-model",
        api_key=None,
        base_url="http://localhost:11434",
        timeout_seconds=3.0,
    )
    adapter = Mock(spec=AnalysisProvider)
    with (
        patch("langchain_ollama.ChatOllama") as chat_ollama,
        patch(
            "casepilot.integrations.llm.provider_factory.LangChainAnalysisProvider",
            return_value=adapter,
        ) as langchain_adapter,
    ):
        result = build_analysis_provider(settings)

    chat_ollama.assert_called_once_with(
        model="test-model",
        base_url="http://localhost:11434",
        client_kwargs={"timeout": 3.0},
        temperature=0,
    )
    langchain_adapter.assert_called_once_with(chat_ollama.return_value)
    assert result is adapter


@pytest.mark.parametrize(
    "provider",
    [LLMProviderKind.OPENAI, LLMProviderKind.OLLAMA],
)
def test_provider_factory_requires_model(provider: LLMProviderKind) -> None:
    settings = LLMProviderSettings(
        provider=provider,
        model=None,
        api_key=SecretStr("test-key") if provider is LLMProviderKind.OPENAI else None,
        base_url=None,
        timeout_seconds=4.0,
    )

    with pytest.raises(ValueError, match="model is required"):
        build_analysis_provider(settings)
