from pydantic import BaseModel, ConfigDict, Field

from casepilot.models import CasePriority


class CaseAnalysis(BaseModel):
    """Human-reviewable analysis and recommendations for a support case."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(
        min_length=1,
        max_length=1000,
        description="A concise summary for a support agent to review.",
    )
    suggested_priority: CasePriority = Field(
        description="A suggested priority; the stored case priority is not changed."
    )
    recommended_next_step: str = Field(
        min_length=1,
        max_length=500,
        description="A possible next step for a support agent to review.",
    )
