from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from casepilot.database import get_session
from casepilot.exceptions.case_not_found_error import CaseNotFoundError
from casepilot.exceptions.customer_not_found_error import CustomerNotFoundError
from casepilot.models import CaseStatus
from casepilot.schemas.case_create_request import CaseCreate
from casepilot.schemas.case_list_response import CaseListResponse
from casepilot.schemas.case_response import CaseResponse
from casepilot.schemas.case_update_request import CaseUpdate
from casepilot.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])
SessionDependency = Annotated[Session, Depends(get_session)]


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(request: CaseCreate, session: SessionDependency) -> CaseResponse:
    try:
        case = CaseService(session).create(request)
        return CaseResponse.model_validate(case)
    except CustomerNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="customer_id does not identify an existing customer",
        ) from error


@router.get("", response_model=CaseListResponse)
def list_cases(
    session: SessionDependency,
    case_status: Annotated[CaseStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CaseListResponse:
    cases, total = CaseService(session).list(
        status=case_status, limit=limit, offset=offset
    )
    return CaseListResponse(
        items=[CaseResponse.model_validate(case) for case in cases],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: UUID, session: SessionDependency) -> CaseResponse:
    try:
        case = CaseService(session).get(case_id)
        return CaseResponse.model_validate(case)
    except CaseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        ) from error


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: UUID, request: CaseUpdate, session: SessionDependency
) -> CaseResponse:
    try:
        case = CaseService(session).update(case_id, request)
        return CaseResponse.model_validate(case)
    except CaseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        ) from error
