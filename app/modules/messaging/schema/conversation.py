import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.modules.messaging.model.conversation import (
    ConversationStatus,
    ConversationType,
)


# Base Schemas
class ConversationBase(SQLModel):
    """Base conversation schema"""

    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    type: ConversationType = Field(default=ConversationType.direct)

    # Conversation settings
    is_encrypted: bool = Field(default=True)
    allow_reactions: bool = Field(default=True)
    allow_voice_messages: bool = Field(default=True)
    allow_video_messages: bool = Field(default=True)
    allow_file_sharing: bool = Field(default=True)

    # Group settings
    max_participants: Optional[int] = Field(default=None, ge=2, le=1000)
    only_admins_can_add: bool = Field(default=False)
    only_admins_can_send: bool = Field(default=False)


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""

    participant_ids: List[uuid.UUID] = Field(
        ..., min_length=1
    )  # Users to add to conversation


class ConversationUpdate(SQLModel):
    """Schema for updating a conversation"""

    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    allow_reactions: Optional[bool] = Field(default=None)
    allow_voice_messages: Optional[bool] = Field(default=None)
    allow_video_messages: Optional[bool] = Field(default=None)
    allow_file_sharing: Optional[bool] = Field(default=None)
    max_participants: Optional[int] = Field(default=None, ge=2, le=1000)
    only_admins_can_add: Optional[bool] = Field(default=None)
    only_admins_can_send: Optional[bool] = Field(default=None)


class ConversationPublic(ConversationBase):
    """Public conversation schema with additional fields"""

    id: uuid.UUID
    creator_id: uuid.UUID
    status: ConversationStatus

    # Computed properties
    is_group: bool
    participant_count: int
    message_count: int

    # Last message info
    last_message_at: Optional[datetime]
    last_message_preview: Optional[str]

    # Timestamps
    created_at: datetime
    updated_at: datetime


class ConversationList(SQLModel):
    """Schema for conversation list response"""

    data: List[ConversationPublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class ConversationWithParticipants(ConversationPublic):
    """Conversation with participant details"""

    participants: List[
        dict
    ]  # [{"user_id": uuid, "role": "admin", "status": "active", ...}]


class ConversationSettings(SQLModel):
    """Schema for conversation settings"""

    allow_reactions: bool
    allow_voice_messages: bool
    allow_video_messages: bool
    allow_file_sharing: bool
    max_participants: Optional[int]
    only_admins_can_add: bool
    only_admins_can_send: bool


class ConversationStats(SQLModel):
    """Schema for conversation statistics"""

    conversation_id: uuid.UUID
    total_messages: int
    total_participants: int
    active_participants: int
    messages_per_day: float
    top_reactions: List[dict]  # [{"emoji": "👍", "count": 10}]
    media_messages_count: int
    voice_messages_count: int
