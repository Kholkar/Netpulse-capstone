from app.events import create_offline_alert
from app.errors import DeviceAlreadyExistsError, DeviceNotFoundError
from app.models import DeviceCreate, DeviceResponse, DeviceStatus
from app.repositories.device_repository import DeviceRepository


class DeviceService:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def register(self, device: DeviceCreate) -> DeviceResponse:
        if self._repository.get_device(device.device_id) is not None:
            raise DeviceAlreadyExistsError(device.device_id)

        response = DeviceResponse.model_validate(device.model_dump())
        return self._repository.add_device(response)

    def list(self) -> list[DeviceResponse]:
        return self._repository.list_devices()

    def get(self, device_id: str) -> DeviceResponse:
        device = self._repository.get_device(device_id)
        if device is None:
            raise DeviceNotFoundError(device_id)
        return device

    def update_status(
        self, device_id: str, status: DeviceStatus
    ) -> DeviceResponse:
        current = self._repository.get_device(device_id)
        if current is None:
            raise DeviceNotFoundError(device_id)

        updated = self._repository.update_status(device_id, status)
        if updated is None:
            raise DeviceNotFoundError(device_id)

        if current.status == DeviceStatus.online and status == DeviceStatus.offline:
            create_offline_alert(self._repository, device_id)

        return updated