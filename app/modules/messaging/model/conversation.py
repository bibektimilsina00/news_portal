import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.shared.enums import ConversationStatus, ConversationType

if TYPE_CHECKING:
    pass


class Conversation(SQLModel, table=True):
    """Conversation/chat model"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Creator
    creator_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Conversation metadata
    title: Optional[str] = Field(default=None, max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    type: ConversationType = Field(default=ConversationType.direct)

    # Conversation settings
    is_group: bool = Field(default=False)
    is_encrypted: bool = Field(default=True)
    allow_reactions: bool = Field(default=True)
    allow_voice_messages: bool = Field(default=True)
    allow_video_messages: bool = Field(default=True)
    allow_file_sharing: bool = Field(default=True)

    # Group settings (only for group chats)
    max_participants: Optional[int] = Field(default=None, ge=2, le=1000)
    only_admins_can_add: bool = Field(default=False)
    only_admins_can_send: bool = Field(default=False)

    # Status and metadata
    status: ConversationStatus = Field(default=ConversationStatus.active)
    last_message_at: Optional[datetime] = Field(default=None, index=True)
    last_message_preview: Optional[str] = Field(default=None, max_length=200)

    # Analytics
    message_count: int = Field(default=0, ge=0)
    participant_count: int = Field(default=0, ge=0)

    # Custom settings
    settings: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    # creator: "User" = Relationship(back_populates="created_conversations")
    # participants: List["ConversationParticipant"] = Relationship(back_populates="conversation")
    # messages: List["Message"] = Relationship(back_populates="conversation")

    # Computed properties
    @property
    def is_direct_chat(self) -> bool:
        """Check if this is a direct one-on-one conversation"""
        return self.type == ConversationType.direct and not self.is_group

    @property
    def is_group_chat(self) -> bool:
        """Check if this is a group conversation"""
        return self.type == ConversationType.group or self.is_group

    @property
    def can_add_participants(self) -> bool:
        """Check if participants can be added to this conversation"""
        if not self.is_group_chat:
            return False
        return self.participant_count < (self.max_participants or 1000)
