from uuid import UUID

from sqlalchemy.orm import Session

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

    def update(
        self,
        case_id: UUID,
        *,
        title: str,
        status: CaseStatus,
        priority: CasePriority,
    ) -> Case | None:
        case = self.get_by_id(case_id)
        if case is None:
            return None

        case.title = title
        case.status = status
        case.priority = priority
        self._session.flush()
        return case
