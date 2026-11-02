from collections.abc import Generator
from typing import Any
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import casepilot.main
from casepilot.daos import CustomerDAO
from casepilot.database import get_session
from casepilot.integrations.llm.dependencies import get_case_analysis_service
from casepilot.integrations.llm.fake_analysis_provider import FakeAnalysisProvider
from casepilot.main import app
from casepilot.models import CasePriority
from casepilot.requests.case_analysis_request import CaseAnalysisRequest
from casepilot.responses.case_analysis_response import CaseAnalysis
from casepilot.services.case_analysis_service import CaseAnalysisService


@pytest.fixture
def api_client(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    monkeypatch.setattr(casepilot.main, "check_database_connection", lambda: None)
    app.dependency_overrides[get_session] = lambda: db_session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def openapi_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    monkeypatch.setattr(casepilot.main, "check_database_connection", lambda: None)
    with TestClient(app) as client:
        yield client


def _create_case(
    api_client: TestClient,
    customer_id: UUID,
    *,
    title: str,
    status: str = "open",
    description: str | None = "Login fails",
) -> Any:
    response = api_client.post(
        "/cases",
        json={
            "customer_id": str(customer_id),
            "title": title,
            "description": description,
            "status": status,
            "priority": "high",
        },
    )
    return response


def _create_customer(db_session: Session) -> UUID:
    return CustomerDAO(db_session).create(name="Contoso").id


def test_openapi_documents_case_methods(openapi_client: TestClient) -> None:
    paths = openapi_client.get("/openapi.json").json()["paths"]

    assert set(paths["/cases"]) == {"get", "post"}
    assert set(paths["/cases/{case_id}"]) == {"get", "patch"}
    assert set(paths["/cases/{case_id}/analysis"]) == {"post"}


def test_create_case_returns_created_case(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)

    response = _create_case(
        api_client, customer_id, title="Cannot sign in", status="open"
    )

    assert response.status_code == 201
    assert response.json()["customer_id"] == str(customer_id)
    assert response.json()["title"] == "Cannot sign in"
    assert response.json()["status"] == "open"


def test_list_cases_filters_by_status(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)
    open_case = _create_case(api_client, customer_id, title="Open case")
    _create_case(api_client, customer_id, title="Closed case", status="closed")

    response = api_client.get("/cases", params={"status": "open"})

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert [item["id"] for item in response.json()["items"]] == [open_case.json()["id"]]


def test_list_cases_paginates_results(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)
    first_case = _create_case(api_client, customer_id, title="First case")
    second_case = _create_case(api_client, customer_id, title="Second case")

    first_page = api_client.get("/cases", params={"limit": 1, "offset": 0})
    second_page = api_client.get("/cases", params={"limit": 1, "offset": 1})

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    first_page_ids = {item["id"] for item in first_page.json()["items"]}
    second_page_ids = {item["id"] for item in second_page.json()["items"]}
    assert first_page.json()["total"] == 2
    assert second_page.json()["total"] == 2
    assert first_page_ids.isdisjoint(second_page_ids)
    assert first_page_ids | second_page_ids == {
        first_case.json()["id"],
        second_case.json()["id"],
    }


def test_get_case_returns_requested_case(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)
    created_case = _create_case(api_client, customer_id, title="Cannot sign in")

    response = api_client.get(f"/cases/{created_case.json()['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created_case.json()["id"]
    assert response.json()["title"] == "Cannot sign in"


def test_patch_case_changes_sent_fields_and_preserves_omitted_fields(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)
    created_case = _create_case(api_client, customer_id, title="Cannot sign in")

    response = api_client.patch(
        f"/cases/{created_case.json()['id']}",
        json={"title": "Login issue", "status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Login issue"
    assert response.json()["status"] == "in_progress"
    assert response.json()["description"] == "Login fails"


def test_patch_case_can_clear_description(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)
    created_case = _create_case(api_client, customer_id, title="Cannot sign in")

    response = api_client.patch(
        f"/cases/{created_case.json()['id']}", json={"description": None}
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/cases/00000000-0000-0000-0000-000000000001"),
        ("patch", "/cases/00000000-0000-0000-0000-000000000001"),
    ],
)
def test_case_endpoints_return_404_for_missing_case(
    api_client: TestClient, method: str, path: str
) -> None:
    request_body = {"title": "Changed"} if method == "patch" else None
    response = api_client.request(method, path, json=request_body)

    assert response.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "Missing customer ID"},
        {
            "customer_id": "00000000-0000-0000-0000-000000000001",
            "title": "Unknown customer",
        },
    ],
)
def test_create_case_returns_422_for_invalid_payload(
    api_client: TestClient, payload: dict[str, str]
) -> None:
    response = api_client.post("/cases", json=payload)

    assert response.status_code == 422


def test_get_case_returns_422_for_malformed_uuid(api_client: TestClient) -> None:
    response = api_client.get("/cases/not-a-uuid")

    assert response.status_code == 422


def test_analysis_endpoint_returns_fake_suggestion_without_changing_case(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)
    created_case = _create_case(
        api_client, customer_id, title="Cannot sign in", description="SSO fails"
    )
    app.dependency_overrides[get_case_analysis_service] = lambda: CaseAnalysisService(
        FakeAnalysisProvider()
    )

    response = api_client.post(f"/cases/{created_case.json()['id']}/analysis")
    case_response = api_client.get(f"/cases/{created_case.json()['id']}")

    assert response.status_code == 200
    assert response.json()["summary"] == "Demo analysis for: Cannot sign in"
    assert response.json()["suggested_priority"] == "medium"
    assert response.json()["recommended_next_step"]
    assert case_response.json()["priority"] == "high"


def test_analysis_endpoint_releases_database_session_before_analysis(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)
    created_case = _create_case(api_client, customer_id, title="Cannot sign in")
    expected = CaseAnalysis(
        summary="Sign-in is failing.",
        suggested_priority=CasePriority.HIGH,
        recommended_next_step="Review the identity-provider configuration.",
    )

    def analyze(request: CaseAnalysisRequest) -> CaseAnalysis:
        assert not db_session.in_transaction()
        return expected

    analysis_service = Mock(spec=CaseAnalysisService)
    analysis_service.analyze.side_effect = analyze
    app.dependency_overrides[get_case_analysis_service] = lambda: analysis_service

    response = api_client.post(f"/cases/{created_case.json()['id']}/analysis")

    assert response.status_code == 200
    assert response.json() == expected.model_dump(mode="json")


def test_analysis_failure_returns_safe_service_unavailable_response(
    api_client: TestClient, db_session: Session
) -> None:
    customer_id = _create_customer(db_session)
    created_case = _create_case(api_client, customer_id, title="Cannot sign in")
    app.dependency_overrides[get_case_analysis_service] = lambda: CaseAnalysisService(
        FakeAnalysisProvider(error=RuntimeError("secret test API key"))
    )

    response = api_client.post(f"/cases/{created_case.json()['id']}/analysis")

    assert response.status_code == 503
    assert "secret test API key" not in response.text


def test_disabled_analysis_does_not_break_case_api(
    api_client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CASEPILOT_LLM_PROVIDER", "disabled")
    customer_id = _create_customer(db_session)
    created_case = _create_case(api_client, customer_id, title="Cannot sign in")

    analysis_response = api_client.post(f"/cases/{created_case.json()['id']}/analysis")
    case_response = api_client.get(f"/cases/{created_case.json()['id']}")

    assert analysis_response.status_code == 503
    assert case_response.status_code == 200


@pytest.mark.parametrize("field", ["status", "priority"])
def test_patch_case_returns_422_for_null_status_and_priority(
    openapi_client: TestClient, field: str
) -> None:
    response = openapi_client.patch(
        "/cases/00000000-0000-0000-0000-000000000001", json={field: None}
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "query_params",
    [
        {"status": "unknown"},
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ],
)
def test_case_list_returns_422_for_invalid_query_parameters(
    api_client: TestClient, query_params: dict[str, str | int]
) -> None:
    response = api_client.get("/cases", params=query_params)

    assert response.status_code == 422
