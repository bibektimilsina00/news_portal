import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.modules.notifications.model.notification import (
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)


class NotificationBase(SQLModel):
    """Base notification schema"""

    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.medium
    status: NotificationStatus = NotificationStatus.pending

    # Optional metadata
    entity_type: Optional[str] = Field(default=None, max_length=50)
    entity_id: Optional[str] = Field(default=None, max_length=100)
    action_url: Optional[str] = Field(default=None, max_length=500)

    # Push notification data
    push_sent_at: Optional[datetime] = None
    push_error: Optional[str] = Field(default=None, max_length=500)

    # Email notification data
    email_sent_at: Optional[datetime] = None
    email_error: Optional[str] = Field(default=None, max_length=500)


class NotificationCreate(NotificationBase):
    """Schema for creating notifications"""

    recipient_id: str
    sender_id: Optional[str] = None

    # Additional metadata
    metadata_: Optional[dict] = None


class NotificationUpdate(SQLModel):
    """Schema for updating notifications"""

    title: Optional[str] = Field(default=None, max_length=200)
    message: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[NotificationStatus] = None
    priority: Optional[NotificationPriority] = None

    # Update tracking
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None

    # Push/Email status updates
    push_sent_at: Optional[datetime] = None
    push_error: Optional[str] = None
    email_sent_at: Optional[datetime] = None
    email_error: Optional[str] = None


class NotificationPublic(NotificationBase):
    """Public notification schema"""

    id: uuid.UUID
    recipient_id: str
    sender_id: Optional[str] = None

    # Read tracking
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Additional metadata
    metadata_: Optional[dict] = None


class NotificationWithSender(NotificationPublic):
    """Notification with sender information"""

    sender: Optional["UserPublic"] = None


class NotificationWithRecipient(NotificationPublic):
    """Notification with recipient information"""

    recipient: "UserPublic"


# Import here to avoid circular imports
from app.modules.users.schema.user import UserPublic
