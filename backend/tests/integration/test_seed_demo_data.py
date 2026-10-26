from sqlalchemy import func, select
from sqlalchemy.orm import Session

from casepilot.models import Case, Customer
from casepilot.seed_demo_data import DEMO_CASES, DEMO_CUSTOMERS, seed_demo_data


def test_seed_demo_data_is_idempotent(db_session: Session) -> None:
    customer_external_ids = [external_id for external_id, _ in DEMO_CUSTOMERS]
    case_external_ids = [case[0] for case in DEMO_CASES]

    seed_demo_data(db_session)
    first_customer_count = db_session.scalar(
        select(func.count())
        .select_from(Customer)
        .where(Customer.external_id.in_(customer_external_ids))
    )
    first_case_count = db_session.scalar(
        select(func.count())
        .select_from(Case)
        .where(Case.external_id.in_(case_external_ids))
    )

    seed_demo_data(db_session)
    second_customer_count = db_session.scalar(
        select(func.count())
        .select_from(Customer)
        .where(Customer.external_id.in_(customer_external_ids))
    )
    second_case_count = db_session.scalar(
        select(func.count())
        .select_from(Case)
        .where(Case.external_id.in_(case_external_ids))
    )

    assert first_customer_count == len(DEMO_CUSTOMERS)
    assert first_case_count == len(DEMO_CASES)
    assert second_customer_count == first_customer_count
    assert second_case_count == first_case_count
