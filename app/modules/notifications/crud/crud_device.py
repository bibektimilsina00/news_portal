from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.notifications.model.device import Device
from app.modules.notifications.schema.device import DeviceCreate, DeviceUpdate
from app.shared.crud.base import CRUDBase


class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    """CRUD operations for devices"""

    def get_by_token(self, session: Session, *, device_token: str) -> Optional[Device]:
        """Get device by token"""
        return session.exec(
            select(Device).where(Device.device_token == device_token)
        ).first()

    def get_by_user(
        self, session: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Device]:
        """Get devices for a specific user"""
        return list(
            session.exec(
                select(Device)
                .where(Device.user_id == user_id)
                .offset(skip)
                .limit(limit)
            )
        )

    def get_active_by_user(self, session: Session, *, user_id: str) -> List[Device]:
        """Get active devices for a specific user"""
        from app.modules.notifications.model.device import DeviceStatus

        return list(
            session.exec(
                select(Device).where(
                    Device.user_id == user_id, Device.status == DeviceStatus.active
                )
            )
        )

    def update_last_active(
        self, session: Session, *, device_id: UUID
    ) -> Optional[Device]:
        """Update device's last active timestamp"""
        device = self.get(session=session, id=device_id)
        if device:
            device.last_active_at = datetime.utcnow()
            session.add(device)
            session.commit()
            session.refresh(device)
            return device
        return None

    def deactivate_device(
        self, session: Session, *, device_id: UUID
    ) -> Optional[Device]:
        """Deactivate a device"""
        from app.modules.notifications.model.device import DeviceStatus

        device = self.get(session=session, id=device_id)
        if device:
            device.status = DeviceStatus.INACTIVE
            device.updated_at = datetime.utcnow()
            session.add(device)
            session.commit()
            session.refresh(device)
            return device
        return None

    def get_stale_devices(
        self, session: Session, *, days_inactive: int = 30
    ) -> List[Device]:
        """Get devices that haven't been active for specified days"""
        from datetime import timedelta

        from app.modules.notifications.model.device import DeviceStatus

        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)

        return list(
            session.exec(
                select(Device).where(
                    Device.status == DeviceStatus.active,
                    Device.last_active_at < cutoff_date,
                )
            )
        )


crud_device = CRUDDevice(Device)
