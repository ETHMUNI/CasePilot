from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from casepilot.api.cases import router as cases_router
from casepilot.database import check_database_connection, engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    check_database_connection()
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(title="CasePilot API", lifespan=lifespan)
app.include_router(cases_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
