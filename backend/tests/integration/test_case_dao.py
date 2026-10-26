from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from casepilot.daos import CaseDAO, CustomerDAO
from casepilot.models import CasePriority, CaseStatus


def test_create_case_persists_customer_relationship_and_values(
    db_session: Session,
) -> None:
    customer = CustomerDAO(db_session).create(name="Contoso")
    case_dao = CaseDAO(db_session)
    case = case_dao.create(
        customer_id=customer.id,
        title="Cannot sign in",
        description="The user receives an error after submitting credentials.",
        status=CaseStatus.OPEN,
        priority=CasePriority.HIGH,
    )
    db_session.commit()

    saved_case = case_dao.get_by_id(case.id)

    assert saved_case is not None
    assert saved_case.customer.id == customer.id
    assert saved_case in customer.cases
    assert saved_case.status is CaseStatus.OPEN
    assert saved_case.priority is CasePriority.HIGH
    assert isinstance(saved_case.created_at, datetime)
    assert isinstance(saved_case.updated_at, datetime)


def test_update_case_persists_changes(db_session: Session) -> None:
    customer = CustomerDAO(db_session).create(name="Contoso")
    case_dao = CaseDAO(db_session)
    case = case_dao.create(
        customer_id=customer.id,
        title="Cannot sign in",
        description="The user receives an error after submitting credentials.",
        status=CaseStatus.OPEN,
        priority=CasePriority.HIGH,
    )
    db_session.commit()

    case_dao.update(
        case.id,
        title="Sign-in failure",
        status=CaseStatus.IN_PROGRESS,
        priority=CasePriority.URGENT,
    )
    db_session.commit()
    updated_case = case_dao.get_by_id(case.id)

    assert updated_case is not None
    assert updated_case.title == "Sign-in failure"
    assert updated_case.status is CaseStatus.IN_PROGRESS
    assert updated_case.priority is CasePriority.URGENT


def test_update_case_can_clear_description(db_session: Session) -> None:
    customer = CustomerDAO(db_session).create(name="Contoso")
    case_dao = CaseDAO(db_session)
    case = case_dao.create(
        customer_id=customer.id,
        title="Cannot sign in",
        description="Login fails",
        status=CaseStatus.OPEN,
        priority=CasePriority.HIGH,
    )

    updated_case = case_dao.update(case.id, description=None)

    assert updated_case is not None
    assert updated_case.description is None


def test_create_case_rejects_unknown_customer_reference(db_session: Session) -> None:
    with pytest.raises(IntegrityError):
        CaseDAO(db_session).create(
            customer_id=uuid4(),
            title="Orphan case",
            description=None,
            status=CaseStatus.OPEN,
            priority=CasePriority.LOW,
        )


def test_create_case_rejects_blank_title(db_session: Session) -> None:
    customer = CustomerDAO(db_session).create(name="Contoso")

    with pytest.raises(IntegrityError):
        CaseDAO(db_session).create(
            customer_id=customer.id,
            title=" ",
            description=None,
            status=CaseStatus.OPEN,
            priority=CasePriority.LOW,
        )
