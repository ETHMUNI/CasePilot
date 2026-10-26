from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from casepilot.daos.unset import UNSET, Unset
from casepilot.models import Case, CasePriority, CaseStatus


class CaseDAO:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        customer_id: UUID,
        title: str,
        description: str | None,
        status: CaseStatus,
        priority: CasePriority,
        external_id: str | None = None,
    ) -> Case:
        case = Case(
            customer_id=customer_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            external_id=external_id,
        )
        self._session.add(case)
        self._session.flush()
        return case

    def get_by_id(self, case_id: UUID) -> Case | None:
        return self._session.get(Case, case_id)

    def list(
        self, *, status: CaseStatus | None, limit: int, offset: int
    ) -> tuple[list[Case], int]:
        statement = select(Case)
        count_statement = select(func.count()).select_from(Case)
        if status is not None:
            statement = statement.where(Case.status == status)
            count_statement = count_statement.where(Case.status == status)
        cases = self._session.scalars(
            statement.order_by(Case.created_at.desc(), Case.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self._session.scalar(count_statement)
        return list(cases), total or 0

    def update(
        self,
        case_id: UUID,
        *,
        title: str | None = None,
        description: str | None | Unset = UNSET,
        status: CaseStatus | None = None,
        priority: CasePriority | None = None,
    ) -> Case | None:
        case = self.get_by_id(case_id)
        if case is None:
            return None

        if title is not None:
            case.title = title
        if not isinstance(description, Unset):
            case.description = description
        if status is not None:
            case.status = status
        if priority is not None:
            case.priority = priority
        self._session.flush()
        return case
