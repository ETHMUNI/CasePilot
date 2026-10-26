from uuid import UUID

from sqlalchemy.orm import Session

from casepilot.daos import CaseDAO, CustomerDAO
from casepilot.database import SessionFactory
from casepilot.models import CasePriority, CaseStatus

type DemoCustomer = tuple[str, str]
type DemoCase = tuple[str, str, str, str, CaseStatus, CasePriority]

DEMO_CUSTOMERS: tuple[DemoCustomer, ...] = (
    ("DEMO-CUSTOMER-001", "Example Retail Demo"),
    ("DEMO-CUSTOMER-002", "Sample Cloud Demo"),
    ("DEMO-CUSTOMER-003", "Fictional Logistics Demo"),
)

DEMO_CASES: tuple[DemoCase, ...] = (
    (
        "DEMO-CASE-001",
        "DEMO-CUSTOMER-001",
        "Single sign-on fails after certificate rotation",
        "Synthetic authentication scenario: the identity provider uses a new "
        "signing certificate that has not yet been synchronized.",
        CaseStatus.OPEN,
        CasePriority.HIGH,
    ),
    (
        "DEMO-CASE-002",
        "DEMO-CUSTOMER-001",
        "Multi-factor challenge repeats after approval",
        "Synthetic authentication scenario: a test user completes the second "
        "factor but is returned to the challenge screen.",
        CaseStatus.IN_PROGRESS,
        CasePriority.MEDIUM,
    ),
    (
        "DEMO-CASE-003",
        "DEMO-CUSTOMER-002",
        "Webhook delivery times out during case synchronization",
        "Synthetic integration scenario: the receiving endpoint times out and "
        "the same event is retried.",
        CaseStatus.OPEN,
        CasePriority.URGENT,
    ),
    (
        "DEMO-CASE-004",
        "DEMO-CUSTOMER-002",
        "CRM contact update is not reflected in CasePilot",
        "Synthetic integration scenario: a successful CRM update is missing "
        "from the next synchronization cycle.",
        CaseStatus.IN_PROGRESS,
        CasePriority.HIGH,
    ),
    (
        "DEMO-CASE-005",
        "DEMO-CUSTOMER-003",
        "Invoice appears twice after a plan change",
        "Synthetic billing scenario: a plan change near the billing boundary "
        "produces two invoice entries for the same period.",
        CaseStatus.OPEN,
        CasePriority.HIGH,
    ),
    (
        "DEMO-CASE-006",
        "DEMO-CUSTOMER-003",
        "Credit is missing after a subscription downgrade",
        "Synthetic billing scenario: the expected prorated credit is absent "
        "from the account ledger.",
        CaseStatus.RESOLVED,
        CasePriority.LOW,
    ),
)


def seed_demo_data(session: Session) -> None:
    customer_dao = CustomerDAO(session)
    case_dao = CaseDAO(session)
    customer_ids: dict[str, UUID] = {}

    for external_id, name in DEMO_CUSTOMERS:
        customer = customer_dao.get_by_external_id(external_id)
        if customer is None:
            customer = customer_dao.create(name=name, external_id=external_id)
        customer_ids[external_id] = customer.id

    for (
        external_id,
        customer_external_id,
        title,
        description,
        status,
        priority,
    ) in DEMO_CASES:
        if case_dao.get_by_external_id(external_id) is None:
            case_dao.create(
                customer_id=customer_ids[customer_external_id],
                title=title,
                description=description,
                status=status,
                priority=priority,
                external_id=external_id,
            )

    session.commit()


def main() -> None:
    with SessionFactory() as session:
        seed_demo_data(session)
    print(
        f"Demo data is ready: {len(DEMO_CUSTOMERS)} customers, {len(DEMO_CASES)} cases."
    )


if __name__ == "__main__":
    main()
