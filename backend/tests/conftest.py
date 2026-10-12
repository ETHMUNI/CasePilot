import os
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine

from casepilot.config import get_settings


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    test_database = os.environ.get("CASEPILOT_TEST_DATABASE")
    if not test_database:
        raise RuntimeError(
            "Set CASEPILOT_TEST_DATABASE to a dedicated database before running "
            "integration tests."
        )

    settings = get_settings()
    if test_database == settings.database_url.database:
        raise RuntimeError(
            "CASEPILOT_TEST_DATABASE must differ from POSTGRES_DB to protect "
            "development data."
        )

    engine = create_engine(
        settings.database_url.set(database=test_database),
        pool_pre_ping=True,
        connect_args={"connect_timeout": 2},
    )
    try:
        yield engine
    finally:
        engine.dispose()
