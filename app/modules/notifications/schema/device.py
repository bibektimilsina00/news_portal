import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.modules.notifications.model.device import DeviceStatus, DeviceType


class DeviceBase(SQLModel):
    """Base device schema"""

    device_token: str = Field(max_length=500)
    device_type: DeviceType
    device_name: Optional[str] = Field(default=None, max_length=100)
    device_model: Optional[str] = Field(default=None, max_length=100)
    os_version: Optional[str] = Field(default=None, max_length=50)
    app_version: Optional[str] = Field(default=None, max_length=50)

    status: DeviceStatus = DeviceStatus.active

    # Location data
    timezone: Optional[str] = Field(default=None, max_length=50)
    language: Optional[str] = Field(default=None, max_length=10)

    # Push notification settings
    push_enabled: bool = True
    sound_enabled: bool = True
    vibration_enabled: bool = True
    badge_count: int = Field(default=0, ge=0)


class DeviceCreate(DeviceBase):
    """Schema for registering devices"""

    user_id: str
    push_service: str = Field(default="fcm", max_length=50)
    push_service_id: Optional[str] = None
    is_sandbox: bool = False

    # Additional metadata
    metadata_: Optional[dict] = None


class DeviceUpdate(SQLModel):
    """Schema for updating devices"""

    device_name: Optional[str] = Field(default=None, max_length=100)
    device_model: Optional[str] = Field(default=None, max_length=100)
    os_version: Optional[str] = Field(default=None, max_length=50)
    app_version: Optional[str] = Field(default=None, max_length=50)

    status: Optional[DeviceStatus] = None

    # Location updates
    timezone: Optional[str] = None
    language: Optional[str] = None

    # Settings updates
    push_enabled: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None

    # Push service updates
    push_service: Optional[str] = Field(default=None, max_length=50)
    push_service_id: Optional[str] = None
    is_sandbox: Optional[bool] = None

    # Additional metadata
    metadata_: Optional[dict] = None


class DevicePublic(DeviceBase):
    """Public device schema"""

    id: str
    user_id: str

    # Tracking
    last_active_at: datetime
    registered_at: datetime
    updated_at: datetime

    # Push service data
    push_service: str
    push_service_id: Optional[str] = None
    is_sandbox: bool

    # Additional metadata
    metadata_: Optional[dict] = None


class DeviceWithUser(DevicePublic):
    """Device with user information"""

    user: "UserPublic"


# Import here to avoid circular imports
from app.modules.users.schema.user import UserPublic
