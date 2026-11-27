from typing import Protocol

from app.models import AlertResponse, DeviceResponse, DeviceStatus


class DeviceRepository(Protocol):
    def add_device(self, device: DeviceResponse) -> DeviceResponse: ...

    def list_devices(self) -> list[DeviceResponse]: ...

    def get_device(self, device_id: str) -> DeviceResponse | None: ...

    def update_status(
        self, device_id: str, status: DeviceStatus
    ) -> DeviceResponse | None: ...

    def save_alert(self, alert: AlertResponse) -> AlertResponse: ...

    def list_alerts(self) -> list[AlertResponse]: ...


class InMemoryDeviceRepository:
    def __init__(self) -> None:
        self._devices: dict[str, DeviceResponse] = {}
        self._alerts: list[AlertResponse] = []

    def add_device(self, device: DeviceResponse) -> DeviceResponse:
        stored = device.model_copy(deep=True)
        self._devices[stored.device_id] = stored
        return stored.model_copy(deep=True)

    def list_devices(self) -> list[DeviceResponse]:
        return [device.model_copy(deep=True) for device in self._devices.values()]

    def get_device(self, device_id: str) -> DeviceResponse | None:
        device = self._devices.get(device_id)
        return device.model_copy(deep=True) if device is not None else None

    def update_status(
        self, device_id: str, status: DeviceStatus
    ) -> DeviceResponse | None:
        current = self._devices.get(device_id)
        if current is None:
            return None

        updated = current.model_copy(update={"status": status}, deep=True)
        self._devices[device_id] = updated
        return updated.model_copy(deep=True)

    def save_alert(self, alert: AlertResponse) -> AlertResponse:
        stored = alert.model_copy(deep=True)
        self._alerts.append(stored)
        return stored.model_copy(deep=True)

    def list_alerts(self) -> list[AlertResponse]:
        return [alert.model_copy(deep=True) for alert in self._alerts]