from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.repositories.device_repository import (
    DeviceRepository,
    InMemoryDeviceRepository,
)
from app.repositories.mysql_device_repository import MySqlDeviceRepository
from app.services.device_service import DeviceService

memory_repository = InMemoryDeviceRepository()


def get_repository(db: Session = Depends(get_db)) -> DeviceRepository:
    if settings.persistence_backend == "mysql":
        return MySqlDeviceRepository(db)
    if settings.persistence_backend == "memory":
        return memory_repository
    raise RuntimeError("PERSISTENCE_BACKEND must be 'memory' or 'mysql'.")


def get_device_service(
    repository: DeviceRepository = Depends(get_repository),
) -> DeviceService:
    return DeviceService(repository)