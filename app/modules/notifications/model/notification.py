import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

from app.shared.enums import NotificationPriority, NotificationStatus, NotificationType

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class NotificationBase(SQLModel):
    """Base notification model"""

    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    type: NotificationType = Field(sa_column=Column(Enum(NotificationType)))
    priority: NotificationPriority = Field(
        default=NotificationPriority.medium,
        sa_column=Column(Enum(NotificationPriority)),
    )
    status: NotificationStatus = Field(
        default=NotificationStatus.pending, sa_column=Column(Enum(NotificationStatus))
    )

    # Optional metadata
    entity_type: Optional[str] = Field(
        default=None, max_length=50
    )  # e.g., "post", "comment", "user"
    entity_id: Optional[uuid.UUID] = Field(
        default=None
    )  # UUID or ID of the related entity
    action_url: Optional[str] = Field(
        default=None, max_length=500
    )  # URL to navigate to when clicked

    # Push notification data
    push_sent_at: Optional[datetime] = Field(default=None)
    push_error: Optional[str] = Field(default=None, max_length=500)

    # Email notification data
    email_sent_at: Optional[datetime] = Field(default=None)
    email_error: Optional[str] = Field(default=None, max_length=500)


class Notification(NotificationBase, table=True):
    """Notification database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign keys
    recipient_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    sender_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", index=True
    )

    # Relationships
    recipient: "User" = Relationship(
        back_populates="received_notifications",
        sa_relationship_kwargs={"foreign_keys": "[Notification.recipient_id]"},
    )
    sender: Optional["User"] = Relationship(
        back_populates="sent_notifications",
        sa_relationship_kwargs={"foreign_keys": "[Notification.sender_id]"},
    )

    # Additional metadata as JSON
    metadata_: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Read tracking
    read_at: Optional[datetime] = Field(default=None)
    clicked_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
