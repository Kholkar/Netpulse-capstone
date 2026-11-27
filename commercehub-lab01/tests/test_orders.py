import pytest
from fastapi.testclient import TestClient

from app.main import app, repository


@pytest.fixture
def client() -> TestClient:
    repository.clear()
    return TestClient(app)


def sample_order() -> dict[str, object]:
    return {
        "customer_name": "Anu",
        "items": [
            {"name": "Notebook", "quantity": 2, "unit_price": 50},
            {"name": "Pen", "quantity": 1, "unit_price": 20},
        ],
    }


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_order_returns_expected_total(client: TestClient) -> None:
    response = client.post("/orders", json=sample_order())
    second_response = client.post("/orders", json=sample_order())

    assert response.status_code == 201
    assert response.json()["order_id"] == 1
    assert response.json()["total"] == 120.0
    assert second_response.json()["order_id"] == 2


def test_list_orders_returns_saved_order(client: TestClient) -> None:
    created = client.post("/orders", json=sample_order()).json()

    response = client.get("/orders")

    assert response.status_code == 200
    assert response.json() == [created]


def test_zero_quantity_returns_validation_error(client: TestClient) -> None:
    invalid_order = {
        "customer_name": "Anu",
        "items": [{"name": "Notebook", "quantity": 0, "unit_price": 50}],
    }

    response = client.post("/orders", json=invalid_order)

    assert response.status_code == 422