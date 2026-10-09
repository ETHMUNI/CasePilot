import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str


def get_settings() -> Settings:
    return Settings(environment=os.environ.get("CASEPILOT_ENV", "development"))
