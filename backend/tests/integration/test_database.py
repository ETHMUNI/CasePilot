from collections.abc import Generator

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

import casepilot.database
from casepilot.database import check_database_connection, get_session


def test_database_connection_succeeds(test_engine: Engine) -> None:
    check_database_connection(test_engine)


def test_session_dependency_closes_session_after_use(
    test_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_factory = sessionmaker(bind=test_engine, expire_on_commit=False)
    monkeypatch.setattr(casepilot.database, "SessionFactory", session_factory)
    session_generator: Generator[Session, None, None] = get_session()
    session = next(session_generator)

    assert session.execute(text("SELECT 1")).scalar_one() == 1

    with pytest.raises(StopIteration):
        next(session_generator)

    assert isinstance(test_engine.pool, QueuePool)
    assert test_engine.pool.checkedout() == 0
