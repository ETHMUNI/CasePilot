from casepilot.integrations.llm.provider_factory import build_analysis_provider
from casepilot.integrations.llm.provider_settings import get_llm_provider_settings
from casepilot.services.case_analysis_service import CaseAnalysisService


def get_case_analysis_service() -> CaseAnalysisService:
    try:
        settings = get_llm_provider_settings()
        provider = build_analysis_provider(settings)
    except (ImportError, ValueError):
        provider = None
    return CaseAnalysisService(provider)
