from langchain_core.language_models.chat_models import BaseChatModel

from casepilot.integrations.llm.langchain_analysis_provider import (
    LangChainAnalysisProvider,
)
from casepilot.integrations.llm.provider_kind import LLMProviderKind
from casepilot.integrations.llm.provider_settings import LLMProviderSettings
from casepilot.services.analysis_provider import AnalysisProvider


def build_analysis_provider(
    settings: LLMProviderSettings,
) -> AnalysisProvider | None:
    if settings.provider is LLMProviderKind.DISABLED:
        return None
    if settings.model is None:
        raise ValueError("An LLM model is required when a provider is enabled.")

    if settings.provider is LLMProviderKind.OPENAI:
        from langchain_openai import ChatOpenAI

        if settings.api_key is None:
            raise ValueError("An API key is required for the OpenAI provider.")
        chat_model: BaseChatModel = ChatOpenAI(
            model=settings.model,
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=settings.timeout_seconds,
            max_retries=0,
            temperature=0,
        )
    else:
        from langchain_ollama import ChatOllama

        chat_model = ChatOllama(
            model=settings.model,
            base_url=settings.base_url,
            client_kwargs={"timeout": settings.timeout_seconds},
            temperature=0,
        )

    return LangChainAnalysisProvider(chat_model)
