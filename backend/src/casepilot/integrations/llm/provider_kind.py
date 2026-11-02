from enum import StrEnum


class LLMProviderKind(StrEnum):
    DISABLED = "disabled"
    OPENAI = "openai"
    OLLAMA = "ollama"
