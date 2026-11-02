from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from casepilot.models import CasePriority, CaseStatus


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    external_id: str | None
    title: str
    description: str | None
    status: CaseStatus
    priority: CasePriority
    created_at: datetime
    updated_at: datetime
