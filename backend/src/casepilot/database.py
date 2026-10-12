from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from casepilot.config import get_settings


class DatabaseConnectionError(RuntimeError):
    """Raised when CasePilot cannot connect to its PostgreSQL database."""


engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionFactory() as session:
        yield session


def check_database_connection(database_engine: Engine = engine) -> None:
    try:
        with database_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise DatabaseConnectionError(
            "Unable to connect to PostgreSQL. Check that Docker Compose is healthy "
            "and the POSTGRES_* settings are correct."
        ) from error
