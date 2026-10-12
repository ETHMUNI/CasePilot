import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from casepilot.database import (
    DatabaseConnectionError,
    check_database_connection,
)


def test_connection_failure_has_clear_message_without_credentials() -> None:
    unreachable_engine = create_engine(
        URL.create(
            "postgresql+psycopg",
            username="test-user",
            password="test-secret",
            host="127.0.0.1",
            port=1,
            database="casepilot_test",
        ),
        connect_args={"connect_timeout": 1},
    )

    try:
        with pytest.raises(DatabaseConnectionError) as error:
            check_database_connection(unreachable_engine)
    finally:
        unreachable_engine.dispose()

    assert "Unable to connect to PostgreSQL" in str(error.value)
    assert "test-secret" not in str(error.value)
