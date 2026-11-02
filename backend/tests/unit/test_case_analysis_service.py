import pytest

from casepilot.exceptions.analysis_unavailable_error import AnalysisUnavailableError
from casepilot.integrations.llm.fake_analysis_provider import FakeAnalysisProvider
from casepilot.models import CasePriority
from casepilot.requests.case_analysis_request import CaseAnalysisRequest
from casepilot.responses.case_analysis_response import CaseAnalysis
from casepilot.services.case_analysis_service import CaseAnalysisService


def test_analysis_service_returns_structured_fake_provider_output() -> None:
    service = CaseAnalysisService(FakeAnalysisProvider())
    request = CaseAnalysisRequest(
        title="Cannot sign in",
        description="Single sign-on fails.",
        current_priority=CasePriority.HIGH,
    )

    result = service.analyze(request)

    assert isinstance(result, CaseAnalysis)
    assert result.summary == "Demo analysis for: Cannot sign in"
    assert result.suggested_priority is CasePriority.MEDIUM


def test_analysis_service_reports_disabled_provider_safely() -> None:
    service = CaseAnalysisService(None)
    request = CaseAnalysisRequest(
        title="Cannot sign in", current_priority=CasePriority.MEDIUM
    )

    with pytest.raises(AnalysisUnavailableError, match="not enabled"):
        service.analyze(request)


def test_analysis_service_does_not_expose_provider_error_details() -> None:
    service = CaseAnalysisService(
        FakeAnalysisProvider(error=RuntimeError("secret test API key"))
    )
    request = CaseAnalysisRequest(
        title="Cannot sign in", current_priority=CasePriority.MEDIUM
    )

    with pytest.raises(AnalysisUnavailableError) as error:
        service.analyze(request)

    assert "secret test API key" not in str(error.value)
