from uuid import UUID

from sqlalchemy.orm import Session

from casepilot.models import Customer


class CustomerDAO:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, *, name: str, external_id: str | None = None) -> Customer:
        customer = Customer(name=name, external_id=external_id)
        self._session.add(customer)
        self._session.flush()
        return customer

    def get_by_id(self, customer_id: UUID) -> Customer | None:
        return self._session.get(Customer, customer_id)

    def update(self, customer_id: UUID, *, name: str) -> Customer | None:
        customer = self.get_by_id(customer_id)
        if customer is None:
            return None

        customer.name = name
        self._session.flush()
        return customer
