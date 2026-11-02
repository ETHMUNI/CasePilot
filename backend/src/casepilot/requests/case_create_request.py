from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from casepilot.models import CasePriority, CaseStatus


class CaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: CaseStatus = CaseStatus.OPEN
    priority: CasePriority = CasePriority.MEDIUM
    external_id: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def title_must_not_be_blank(self) -> "CaseCreate":
        if not self.title.strip():
            raise ValueError("title must not be blank")
        return self
