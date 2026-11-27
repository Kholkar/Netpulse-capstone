from datetime import timezone
from ipaddress import IPv4Address

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import AlertORM, DeviceORM
from app.errors import DeviceAlreadyExistsError
from app.models import (
    AlertResponse,
    DeviceResponse,
    DeviceStatus,
    DeviceType,
)


class MySqlDeviceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_device(record: DeviceORM) -> DeviceResponse:
        return DeviceResponse(
            device_id=record.device_id,
            name=record.name,
            device_type=DeviceType(record.device_type),
            ip_address=IPv4Address(record.ip_address),
            status=DeviceStatus(record.status),
        )

    @staticmethod
    def _to_alert(record: AlertORM) -> AlertResponse:
        timestamp = record.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        else:
            timestamp = timestamp.astimezone(timezone.utc)

        return AlertResponse(
            device_id=record.device_id,
            message=record.message,
            timestamp=timestamp,
        )

    def add_device(self, device: DeviceResponse) -> DeviceResponse:
        record = DeviceORM(
            device_id=device.device_id,
            name=device.name,
            device_type=device.device_type.value,
            ip_address=str(device.ip_address),
            status=device.status.value,
        )
        self._session.add(record)
        try:
            self._session.commit()
            self._session.refresh(record)
        except IntegrityError as error:
            self._session.rollback()
            raise DeviceAlreadyExistsError(device.device_id) from error
        except SQLAlchemyError:
            self._session.rollback()
            raise
        return self._to_device(record)

    def list_devices(self) -> list[DeviceResponse]:
        records = self._session.scalars(
            select(DeviceORM).order_by(DeviceORM.device_id)
        ).all()
        return [self._to_device(record) for record in records]

    def get_device(self, device_id: str) -> DeviceResponse | None:
        record = self._session.get(DeviceORM, device_id)
        return self._to_device(record) if record is not None else None

    def update_status(
        self, device_id: str, status: DeviceStatus
    ) -> DeviceResponse | None:
        record = self._session.get(DeviceORM, device_id)
        if record is None:
            return None

        record.status = status.value
        try:
            self._session.commit()
            self._session.refresh(record)
        except SQLAlchemyError:
            self._session.rollback()
            raise
        return self._to_device(record)

    def save_alert(self, alert: AlertResponse) -> AlertResponse:
        timestamp = alert.timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        record = AlertORM(
            device_id=alert.device_id,
            message=alert.message,
            timestamp=timestamp,
        )
        self._session.add(record)
        try:
            self._session.commit()
            self._session.refresh(record)
        except SQLAlchemyError:
            self._session.rollback()
            raise
        return self._to_alert(record)

    def list_alerts(self) -> list[AlertResponse]:
        records = self._session.scalars(
            select(AlertORM).order_by(AlertORM.id)
        ).all()
        return [self._to_alert(record) for record in records]