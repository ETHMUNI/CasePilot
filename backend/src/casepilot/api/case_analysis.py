from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from casepilot.database import get_session
from casepilot.exceptions.analysis_unavailable_error import AnalysisUnavailableError
from casepilot.exceptions.case_not_found_error import CaseNotFoundError
from casepilot.integrations.llm.dependencies import get_case_analysis_service
from casepilot.requests.case_analysis_request import CaseAnalysisRequest
from casepilot.responses.case_analysis_response import CaseAnalysis
from casepilot.services.case_analysis_service import CaseAnalysisService
from casepilot.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["case analysis"])
SessionDependency = Annotated[Session, Depends(get_session)]
AnalysisServiceDependency = Annotated[
    CaseAnalysisService, Depends(get_case_analysis_service)
]


@router.post("/{case_id}/analysis", response_model=CaseAnalysis)
def analyze_case(
    case_id: UUID,
    session: SessionDependency,
    analysis_service: AnalysisServiceDependency,
) -> CaseAnalysis:
    try:
        case = CaseService(session).get(case_id)
    except CaseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        ) from error

    request = CaseAnalysisRequest(
        title=case.title,
        description=case.description,
        current_priority=case.priority,
    )
    try:
        return analysis_service.analyze(request)
    except AnalysisUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Case analysis is currently unavailable.",
        ) from error
