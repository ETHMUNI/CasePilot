from pydantic import BaseModel, ConfigDict, Field

from casepilot.models import CasePriority


class CaseAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    current_priority: CasePriority
