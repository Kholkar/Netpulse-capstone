from datetime import timezone

import pytest

from app.models import DeviceCreate, DeviceStatus
from app.repositories.device_repository import InMemoryDeviceRepository
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    DeviceService,
)


@pytest.fixture
def repository() -> InMemoryDeviceRepository:
    return InMemoryDeviceRepository()


@pytest.fixture
def device_service(repository: InMemoryDeviceRepository) -> DeviceService:
    return DeviceService(repository)


def sample_device(
    device_id: str = "RTR-101",
    status: DeviceStatus = DeviceStatus.online,
) -> DeviceCreate:
    return DeviceCreate(
        device_id=device_id,
        name="Branch Router",
        device_type="router",
        ip_address="192.168.10.1",
        status=status,
    )


def test_register_and_list_device(device_service: DeviceService) -> None:
    created = device_service.register(sample_device())

    assert created.device_id == "RTR-101"
    assert created.status == DeviceStatus.online
    assert device_service.list() == [created]


def test_duplicate_device_id_is_rejected(device_service: DeviceService) -> None:
    device_service.register(sample_device())

    with pytest.raises(DeviceAlreadyExistsError):
        device_service.register(sample_device())


def test_missing_device_operations_raise(device_service: DeviceService) -> None:
    with pytest.raises(DeviceNotFoundError):
        device_service.get("unknown")
    with pytest.raises(DeviceNotFoundError):
        device_service.update_status("unknown", DeviceStatus.offline)


def test_registering_offline_device_does_not_alert(
    device_service: DeviceService,
    repository: InMemoryDeviceRepository,
) -> None:
    device_service.register(sample_device(status=DeviceStatus.offline))

    assert repository.list_alerts() == []


def test_online_to_offline_transition_creates_utc_alert(
    device_service: DeviceService,
    repository: InMemoryDeviceRepository,
) -> None:
    device_service.register(sample_device())

    updated = device_service.update_status("RTR-101", DeviceStatus.offline)
    alerts = repository.list_alerts()

    assert updated.status == DeviceStatus.offline
    assert len(alerts) == 1
    assert alerts[0].device_id == "RTR-101"
    assert "went offline" in alerts[0].message
    assert alerts[0].timestamp.tzinfo == timezone.utc


def test_repeated_offline_status_creates_only_one_alert(
    device_service: DeviceService,
    repository: InMemoryDeviceRepository,
) -> None:
    device_service.register(sample_device())
    device_service.update_status("RTR-101", DeviceStatus.offline)
    device_service.update_status("RTR-101", DeviceStatus.offline)

    assert len(repository.list_alerts()) == 1