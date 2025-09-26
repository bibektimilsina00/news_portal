import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.modules.messaging.model.participant import ParticipantRole, ParticipantStatus


# Base Schemas
class ConversationParticipantBase(SQLModel):
    """Base conversation participant schema"""

    role: ParticipantRole = Field(default=ParticipantRole.member)

    # Permissions
    can_send_messages: bool = Field(default=True)
    can_add_participants: bool = Field(default=True)
    can_remove_participants: bool = Field(default=False)
    can_change_settings: bool = Field(default=False)
    can_delete_messages: bool = Field(default=False)

    # Notification settings
    notifications_enabled: bool = Field(default=True)
    notification_sound: bool = Field(default=True)
    notification_preview: bool = Field(default=True)

    # Custom settings
    nickname: Optional[str] = Field(default=None, max_length=50)
    theme_preference: Optional[str] = Field(default=None, max_length=50)


class ConversationParticipantCreate(ConversationParticipantBase):
    """Schema for adding a participant to a conversation"""

    user_id: uuid.UUID
    conversation_id: uuid.UUID


class ConversationParticipantUpdate(SQLModel):
    """Schema for updating a participant"""

    role: Optional[ParticipantRole] = Field(default=None)
    can_send_messages: Optional[bool] = Field(default=None)
    can_add_participants: Optional[bool] = Field(default=None)
    can_remove_participants: Optional[bool] = Field(default=None)
    can_change_settings: Optional[bool] = Field(default=None)
    can_delete_messages: Optional[bool] = Field(default=None)
    notifications_enabled: Optional[bool] = Field(default=None)
    notification_sound: Optional[bool] = Field(default=None)
    notification_preview: Optional[bool] = Field(default=None)
    nickname: Optional[str] = Field(default=None, max_length=50)
    theme_preference: Optional[str] = Field(default=None, max_length=50)


class ConversationParticipantPublic(ConversationParticipantBase):
    """Public participant schema with additional fields"""

    id: uuid.UUID
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    status: ParticipantStatus

    # Activity tracking
    last_seen_at: Optional[datetime]
    joined_at: datetime
    left_at: Optional[datetime]

    # Message tracking
    unread_count: int
    last_read_message_id: Optional[uuid.UUID]

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_active: bool
    is_admin: bool
    is_owner: bool
    can_moderate: bool
    display_name: str


class ConversationParticipantList(SQLModel):
    """Schema for participant list response"""

    data: List[ConversationParticipantPublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class ParticipantAction(SQLModel):
    """Schema for participant actions"""

    participant_id: uuid.UUID
    action: str = Field(
        ...,
        description="Action to perform: promote, demote, mute, unmute, ban, unban, remove",
    )


class BulkParticipantAction(SQLModel):
    """Schema for bulk participant actions"""

    participant_ids: List[uuid.UUID] = Field(..., min_length=1)
    action: str = Field(..., description="Action to perform on all participants")


class ParticipantPermissions(SQLModel):
    """Schema for participant permissions"""

    can_send_messages: bool
    can_add_participants: bool
    can_remove_participants: bool
    can_change_settings: bool
    can_delete_messages: bool


class ParticipantNotificationSettings(SQLModel):
    """Schema for participant notification settings"""

    notifications_enabled: bool
    notification_sound: bool
    notification_preview: bool


class ParticipantStats(SQLModel):
    """Schema for participant statistics"""

    conversation_id: uuid.UUID
    total_participants: int
    active_participants: int
    admins_count: int
    muted_count: int
    banned_count: int
    average_unread_count: float
    most_active_participant: Optional[uuid.UUID]
    participants_by_role: dict  # {"member": 10, "admin": 2, "owner": 1}
    join_leave_activity: List[dict]  # [{"date": "2025-01-01", "joins": 5, "leaves": 2}]
