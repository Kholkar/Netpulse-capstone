import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_repository
from app.main import app
from app.repositories.device_repository import InMemoryDeviceRepository


@pytest.fixture
def client() -> TestClient:
    repository = InMemoryDeviceRepository()
    app.dependency_overrides[get_repository] = lambda: repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_and_offline_alert_flow(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}

    created = client.post(
        "/devices",
        json={
            "device_id": "RTR-101",
            "name": "Branch Router",
            "device_type": "router",
            "ip_address": "192.168.10.1",
            "status": "online",
        },
    )
    assert created.status_code == 201

    for _ in range(2):
        updated = client.patch(
            "/devices/RTR-101/status", json={"status": "offline"}
        )
        assert updated.status_code == 200

    alerts = client.get("/alerts")
    assert alerts.status_code == 200
    assert len(alerts.json()) == 1