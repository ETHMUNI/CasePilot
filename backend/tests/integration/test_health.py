import pytest
from fastapi.testclient import TestClient

import casepilot.main
from casepilot.main import app


def test_health_endpoint_returns_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(casepilot.main, "check_database_connection", lambda: None)

    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
