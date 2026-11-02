from casepilot.exceptions.analysis_unavailable_error import AnalysisUnavailableError
from casepilot.requests.case_analysis_request import CaseAnalysisRequest
from casepilot.responses.case_analysis_response import CaseAnalysis
from casepilot.services.analysis_provider import AnalysisProvider


class CaseAnalysisService:
    def __init__(self, provider: AnalysisProvider | None) -> None:
        self._provider = provider

    def analyze(self, request: CaseAnalysisRequest) -> CaseAnalysis:
        if self._provider is None:
            raise AnalysisUnavailableError("Case analysis is not enabled.")

        try:
            result = self._provider.analyze(request)
            return CaseAnalysis.model_validate(result)
        except Exception:
            raise AnalysisUnavailableError(
                "Case analysis is currently unavailable."
            ) from None
