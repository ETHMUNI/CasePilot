import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from casepilot.daos import CustomerDAO


def test_create_customer_persists_name_and_created_at(db_session: Session) -> None:
    customer_dao = CustomerDAO(db_session)
    customer = customer_dao.create(name="Northwind", external_id="northwind-1")
    db_session.commit()

    saved_customer = customer_dao.get_by_id(customer.id)

    assert saved_customer is not None
    assert saved_customer.name == "Northwind"
    assert saved_customer.created_at is not None


def test_update_customer_persists_new_name(db_session: Session) -> None:
    customer_dao = CustomerDAO(db_session)
    customer = customer_dao.create(name="Northwind")
    db_session.commit()

    customer_dao.update(customer.id, name="Northwind Trading")
    db_session.commit()
    updated_customer = customer_dao.get_by_id(customer.id)

    assert updated_customer is not None
    assert updated_customer.name == "Northwind Trading"


def test_create_customer_rejects_blank_name(db_session: Session) -> None:
    with pytest.raises(IntegrityError):
        CustomerDAO(db_session).create(name=" ")
