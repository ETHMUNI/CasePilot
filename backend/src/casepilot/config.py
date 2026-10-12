import os
from dataclasses import dataclass

from sqlalchemy.engine import URL


@dataclass(frozen=True)
class Settings:
    environment: str
    database_url: URL


def get_settings() -> Settings:
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        raise ValueError(
            "POSTGRES_PASSWORD must be set before starting the application."
        )

    try:
        port = int(os.environ.get("POSTGRES_PORT", "5432"))
    except ValueError as error:
        raise ValueError("POSTGRES_PORT must be an integer.") from error

    if not 1 <= port <= 65535:
        raise ValueError("POSTGRES_PORT must be between 1 and 65535.")

    return Settings(
        environment=os.environ.get("CASEPILOT_ENV", "development"),
        database_url=URL.create(
            drivername="postgresql+psycopg",
            username=os.environ.get("POSTGRES_USER", "casepilot"),
            password=password,
            host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            port=port,
            database=os.environ.get("POSTGRES_DB", "casepilot"),
        ),
    )
