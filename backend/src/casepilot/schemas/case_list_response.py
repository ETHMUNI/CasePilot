from pydantic import BaseModel

from casepilot.schemas.case_response import CaseResponse


class CaseListResponse(BaseModel):
    items: list[CaseResponse]
    total: int
    limit: int
    offset: int
