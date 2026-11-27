from datetime import datetime, timezone
from ipaddress import IPv4Address

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.models import Base
from app.errors import DeviceAlreadyExistsError
from app.models import (
    AlertResponse,
    DeviceCreate,
    DeviceResponse,
    DeviceStatus,
    DeviceType,
)
from app.repositories.mysql_device_repository import MySqlDeviceRepository
from app.services.device_service import DeviceService


@pytest.fixture
def repository() -> MySqlDeviceRepository:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield MySqlDeviceRepository(session)
    engine.dispose()


def sample_device(status: DeviceStatus = DeviceStatus.online) -> DeviceResponse:
    return DeviceResponse(
        device_id="RTR-101",
        name="Branch Router",
        device_type=DeviceType.router,
        ip_address=IPv4Address("192.168.10.1"),
        status=status,
    )


def test_mysql_repository_device_crud_and_duplicate_guard(
    repository: MySqlDeviceRepository,
) -> None:
    created = repository.add_device(sample_device())

    assert repository.get_device("RTR-101") == created
    assert repository.list_devices() == [created]
    with pytest.raises(DeviceAlreadyExistsError):
        repository.add_device(sample_device())

    updated = repository.update_status("RTR-101", DeviceStatus.offline)
    assert updated is not None
    assert updated.status == DeviceStatus.offline
    assert repository.update_status("missing", DeviceStatus.offline) is None


def test_mysql_repository_persists_alert_with_utc_timestamp(
    repository: MySqlDeviceRepository,
) -> None:
    repository.add_device(sample_device())
    alert = AlertResponse(
        device_id="RTR-101",
        message="Device RTR-101 went offline.",
        timestamp=datetime.now(timezone.utc),
    )

    saved = repository.save_alert(alert)

    assert saved.device_id == "RTR-101"
    assert saved.timestamp.tzinfo == timezone.utc
    assert repository.list_alerts() == [saved]


def test_device_service_uses_mysql_repository_for_offline_alerts(
    repository: MySqlDeviceRepository,
) -> None:
    service = DeviceService(repository)
    service.register(
        DeviceCreate(
            device_id="RTR-101",
            name="Branch Router",
            device_type="router",
            ip_address="192.168.10.1",
            status=DeviceStatus.online,
        )
    )

    service.update_status("RTR-101", DeviceStatus.offline)
    service.update_status("RTR-101", DeviceStatus.offline)

    alerts = repository.list_alerts()
    assert len(alerts) == 1
    assert alerts[0].timestamp.tzinfo == timezone.utc