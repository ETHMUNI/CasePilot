from typing import Protocol

from casepilot.requests.case_analysis_request import CaseAnalysisRequest
from casepilot.responses.case_analysis_response import CaseAnalysis


class AnalysisProvider(Protocol):
    def analyze(self, request: CaseAnalysisRequest) -> CaseAnalysis: ...
