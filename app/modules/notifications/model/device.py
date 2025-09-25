import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class DeviceType(str, enum.Enum):
    """Types of devices for push notifications"""

    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    DESKTOP = "desktop"


class DeviceStatus(str, enum.Enum):
    """Device registration status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class DeviceBase(SQLModel):
    """Base device model"""

    device_token: str = Field(unique=True, index=True, max_length=500)  # FCM/APNs token
    device_type: DeviceType = Field(sa_column=Column(Enum(DeviceType)))
    device_name: Optional[str] = Field(
        default=None, max_length=100
    )  # e.g., "iPhone 12", "Chrome Browser"
    device_model: Optional[str] = Field(
        default=None, max_length=100
    )  # e.g., "iPhone12,1"
    os_version: Optional[str] = Field(default=None, max_length=50)  # e.g., "iOS 15.2"
    app_version: Optional[str] = Field(default=None, max_length=50)  # App version

    status: DeviceStatus = Field(
        default=DeviceStatus.ACTIVE, sa_column=Column(Enum(DeviceStatus))
    )

    # Location data (optional, for geo-targeted notifications)
    timezone: Optional[str] = Field(default=None, max_length=50)
    language: Optional[str] = Field(default=None, max_length=10)  # ISO language code

    # Push notification settings
    push_enabled: bool = Field(default=True)
    sound_enabled: bool = Field(default=True)
    vibration_enabled: bool = Field(default=True)
    badge_count: int = Field(default=0, ge=0)  # Unread notification count


class Device(DeviceBase, table=True):
    """Device database model"""

    __tablename__ = "devices"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    # Foreign key
    user_id: str = Field(foreign_key="user.id", index=True)

    # Relationship
    user: "User" = Relationship(back_populates="devices")

    # Device metadata
    metadata_: Optional[dict] = Field(
        default=None, sa_column=Column(JSON)
    )  # Additional device info

    # Tracking
    last_active_at: datetime = Field(default_factory=datetime.utcnow)
    registered_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Push service data
    push_service: str = Field(default="fcm", max_length=50)  # "fcm", "apns", etc.
    push_service_id: Optional[str] = Field(
        default=None, max_length=200
    )  # Service-specific ID

    # Security
    is_sandbox: bool = Field(default=False)  # For iOS sandbox vs production
