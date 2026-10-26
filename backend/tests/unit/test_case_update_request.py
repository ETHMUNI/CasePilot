import pytest
from pydantic import ValidationError

from casepilot.schemas.case_update_request import CaseUpdate


@pytest.mark.parametrize("field", ["status", "priority"])
def test_case_update_rejects_null_status_and_priority(field: str) -> None:
    with pytest.raises(ValidationError):
        CaseUpdate.model_validate({field: None})


def test_case_update_allows_null_description() -> None:
    request = CaseUpdate.model_validate({"description": None})

    assert request.description is None
