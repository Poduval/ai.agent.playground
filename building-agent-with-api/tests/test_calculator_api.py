import pytest
from fastapi.testclient import TestClient

from calculator.api.main import app

client = TestClient(app)
AUTH = {"X-API-Key": "test-key"}


@pytest.mark.parametrize(
    ("op", "a", "b", "expected"),
    [("add", 6, 7, 13), ("subtract", 6, 7, -1), ("multiply", 6, 7, 42), ("divide", 84, 2, 42)],
)
def test_operations(op, a, b, expected):
    response = client.post(f"/{op}", json={"a": a, "b": b}, headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {"operation": op, "result": expected}


def test_divide_by_zero_is_a_client_error():
    response = client.post("/divide", json={"a": 1, "b": 0}, headers=AUTH)
    assert response.status_code == 400
    assert "zero" in response.json()["detail"]


def test_missing_number_is_rejected():
    assert client.post("/add", json={"a": 1}, headers=AUTH).status_code == 422


def test_api_key_required():
    assert client.post("/add", json={"a": 1, "b": 2}).status_code == 401
    assert client.post("/add", json={"a": 1, "b": 2}, headers={"X-API-Key": "wrong"}).status_code == 401


def test_health_is_public():
    assert client.get("/health").json() == {"status": "ok"}
