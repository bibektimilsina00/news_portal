import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.shared.enums import MessageStatus, MessageType

if TYPE_CHECKING:
    pass


class Message(SQLModel, table=True):
    """Message model"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True)
    sender_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Message content
    type: MessageType = Field(default=MessageType.text)
    content: Optional[str] = Field(
        default=None, max_length=10000
    )  # Text content or caption

    # Media attachments
    media_url: Optional[str] = Field(default=None, max_length=1000)
    media_type: Optional[str] = Field(default=None, max_length=100)  # MIME type
    media_size: Optional[int] = Field(default=None, ge=0)  # File size in bytes
    media_duration: Optional[int] = Field(
        default=None, ge=0
    )  # Duration for audio/video in seconds

    # Message metadata
    reply_to_message_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="message.id"
    )
    forwarded_from: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")

    # Status and delivery
    status: MessageStatus = Field(default=MessageStatus.sending)
    delivered_at: Optional[datetime] = Field(default=None)
    read_at: Optional[datetime] = Field(default=None)

    # Message features
    is_edited: bool = Field(default=False)
    edited_at: Optional[datetime] = Field(default=None)
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)

    # Scheduling and disappearing
    scheduled_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)  # For disappearing messages

    # Reactions and interactions
    reactions: List[dict] = Field(
        default_factory=list, sa_column=Column(JSON)
    )  # [{"emoji": "👍", "users": ["user_id1", "user_id2"]}]
    reaction_count: int = Field(default=0, ge=0)

    # Additional metadata
    extra_data: dict = Field(
        default_factory=dict, sa_column=Column(JSON)
    )  # Location data, contact info, etc.

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    # conversation: "Conversation" = Relationship(back_populates="messages")
    # sender: "User" = Relationship(back_populates="sent_messages")
    # reply_to: Optional["Message"] = Relationship()
    # forwarded_from_user: Optional["User"] = Relationship()

    # Computed properties
    @property
    def is_media_message(self) -> bool:
        """Check if this is a media message"""
        return self.type in [
            MessageType.image,
            MessageType.video,
            MessageType.audio,
            MessageType.file,
            MessageType.voice,
        ]

    @property
    def is_system_message(self) -> bool:
        """Check if this is a system message"""
        return self.type == MessageType.system

    @property
    def is_expired(self) -> bool:
        """Check if this message has expired (for disappearing messages)"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_scheduled(self) -> bool:
        """Check if this message is scheduled for future sending"""
        if not self.scheduled_at:
            return False
        return self.scheduled_at > datetime.utcnow()

    @property
    def delivery_status(self) -> str:
        """Get human-readable delivery status"""
        return self.status.value.title()
