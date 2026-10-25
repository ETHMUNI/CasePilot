from pydantic import BaseModel, ConfigDict, Field, model_validator

from casepilot.models import CasePriority, CaseStatus


class CaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: CaseStatus | None = None
    priority: CasePriority | None = None

    @model_validator(mode="after")
    def require_a_change(self) -> "CaseUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title must not be null")
        if self.title is not None and not self.title.strip():
            raise ValueError("title must not be blank")
        return self
