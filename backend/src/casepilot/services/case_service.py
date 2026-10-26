from uuid import UUID

from sqlalchemy.orm import Session

from casepilot.daos import CaseDAO, CustomerDAO
from casepilot.daos.unset import UNSET
from casepilot.exceptions.case_not_found_error import CaseNotFoundError
from casepilot.exceptions.customer_not_found_error import CustomerNotFoundError
from casepilot.models import Case, CaseStatus
from casepilot.schemas.case_create_request import CaseCreate
from casepilot.schemas.case_update_request import CaseUpdate


class CaseService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._cases = CaseDAO(session)
        self._customers = CustomerDAO(session)

    def create(self, request: CaseCreate) -> Case:
        if self._customers.get_by_id(request.customer_id) is None:
            raise CustomerNotFoundError(
                f"Customer {request.customer_id} does not exist"
            )
        case = self._cases.create(
            customer_id=request.customer_id,
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            external_id=request.external_id,
        )
        self._session.commit()
        return case

    def list(
        self, *, status: CaseStatus | None, limit: int, offset: int
    ) -> tuple[list[Case], int]:
        return self._cases.list(status=status, limit=limit, offset=offset)

    def get(self, case_id: UUID) -> Case:
        case = self._cases.get_by_id(case_id)
        if case is None:
            raise CaseNotFoundError(f"Case {case_id} does not exist")
        return case

    def update(self, case_id: UUID, request: CaseUpdate) -> Case:
        description = (
            request.description if "description" in request.model_fields_set else UNSET
        )
        case = self._cases.update(
            case_id,
            title=request.title,
            description=description,
            status=request.status,
            priority=request.priority,
        )
        if case is None:
            raise CaseNotFoundError(f"Case {case_id} does not exist")
        self._session.commit()
        return case
