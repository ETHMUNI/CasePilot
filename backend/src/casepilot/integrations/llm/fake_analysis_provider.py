from casepilot.models import CasePriority
from casepilot.requests.case_analysis_request import CaseAnalysisRequest
from casepilot.responses.case_analysis_response import CaseAnalysis


class FakeAnalysisProvider:
    def __init__(self, error: Exception | None = None) -> None:
        self._error = error

    def analyze(self, request: CaseAnalysisRequest) -> CaseAnalysis:
        if self._error is not None:
            raise self._error
        return CaseAnalysis(
            summary=f"Demo analysis for: {request.title}",
            suggested_priority=CasePriority.MEDIUM,
            recommended_next_step="Review the case details with a support agent.",
        )
