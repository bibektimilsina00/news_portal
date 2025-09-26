import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.modules.messaging.model.message import MessageStatus, MessageType


# Base Schemas
class MessageBase(SQLModel):
    """Base message schema"""

    type: MessageType = Field(default=MessageType.text)
    content: Optional[str] = Field(default=None, max_length=10000)

    # Media attachments
    media_url: Optional[str] = Field(default=None, max_length=1000)
    media_type: Optional[str] = Field(default=None, max_length=100)
    media_size: Optional[int] = Field(default=None, ge=0)
    media_duration: Optional[int] = Field(default=None, ge=0)

    # Message features
    reply_to_message_id: Optional[uuid.UUID] = Field(default=None)
    forwarded_from: Optional[uuid.UUID] = Field(default=None)

    # Scheduling and disappearing
    scheduled_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)


class MessageCreate(MessageBase):
    """Schema for creating a new message"""

    conversation_id: uuid.UUID


class MessageUpdate(SQLModel):
    """Schema for updating a message"""

    content: Optional[str] = Field(default=None, max_length=10000)
    scheduled_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)


class MessagePublic(MessageBase):
    """Public message schema with additional fields"""

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID

    # Status and delivery
    status: MessageStatus
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]

    # Message features
    is_edited: bool
    edited_at: Optional[datetime]
    is_deleted: bool

    # Reactions and interactions
    reactions: List[dict]
    reaction_count: int

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_media_message: bool
    is_system_message: bool
    is_expired: bool
    is_scheduled: bool
    delivery_status: str


class MessageList(SQLModel):
    """Schema for message list response"""

    data: List[MessagePublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class MessageReaction(SQLModel):
    """Schema for adding/removing message reactions"""

    emoji: str = Field(..., max_length=10)


class MessageForward(SQLModel):
    """Schema for forwarding messages"""

    to_conversation_ids: List[uuid.UUID] = Field(..., min_length=1)


class MessageSearch(SQLModel):
    """Schema for searching messages"""

    query: str = Field(..., min_length=1, max_length=100)
    conversation_id: Optional[uuid.UUID] = Field(default=None)
    sender_id: Optional[uuid.UUID] = Field(default=None)
    message_type: Optional[MessageType] = Field(default=None)
    from_date: Optional[datetime] = Field(default=None)
    to_date: Optional[datetime] = Field(default=None)


class MessageSearchResult(SQLModel):
    """Schema for message search results"""

    message: MessagePublic
    conversation_title: Optional[str]
    sender_name: Optional[str]
    highlights: List[str]  # Search result highlights


class MessageStats(SQLModel):
    """Schema for message statistics"""

    conversation_id: uuid.UUID
    total_messages: int
    messages_by_type: dict  # {"text": 100, "image": 20, "video": 5}
    messages_by_sender: List[dict]  # [{"user_id": uuid, "count": 50}]
    daily_message_count: List[dict]  # [{"date": "2025-01-01", "count": 10}]
    average_messages_per_day: float
    most_active_hour: int  # 0-23
    top_reactions: List[dict]  # [{"emoji": "👍", "count": 25}]
