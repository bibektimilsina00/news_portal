import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Enum, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.messaging.model.conversation import Conversation
    from app.modules.users.model.user import User


class ParticipantRole(str, enum.Enum):
    """Participant roles in conversations"""

    MEMBER = "member"  # Regular member
    ADMIN = "admin"  # Group admin
    OWNER = "owner"  # Conversation owner/creator


class ParticipantStatus(str, enum.Enum):
    """Participant status"""

    ACTIVE = "active"
    MUTED = "muted"
    BANNED = "banned"
    LEFT = "left"


class ConversationParticipant(SQLModel, table=True):
    """Conversation participant model"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Participant info
    role: ParticipantRole = Field(default=ParticipantRole.MEMBER)
    status: ParticipantStatus = Field(default=ParticipantStatus.ACTIVE)

    # Permissions and settings
    can_send_messages: bool = Field(default=True)
    can_add_participants: bool = Field(default=True)
    can_remove_participants: bool = Field(default=False)
    can_change_settings: bool = Field(default=False)
    can_delete_messages: bool = Field(default=False)

    # Notification settings
    notifications_enabled: bool = Field(default=True)
    notification_sound: bool = Field(default=True)
    notification_preview: bool = Field(default=True)

    # Activity tracking
    last_seen_at: Optional[datetime] = Field(default=None)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = Field(default=None)

    # Message tracking
    unread_count: int = Field(default=0, ge=0)
    last_read_message_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="message.id"
    )

    # Custom settings
    nickname: Optional[str] = Field(
        default=None, max_length=50
    )  # Custom nickname in this conversation
    theme_preference: Optional[str] = Field(default=None, max_length=50)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    # conversation: "Conversation" = Relationship(back_populates="participants")
    # user: "User" = Relationship(back_populates="conversation_participations")

    # Computed properties
    @property
    def is_active(self) -> bool:
        """Check if participant is currently active"""
        return self.status == ParticipantStatus.ACTIVE

    @property
    def is_admin(self) -> bool:
        """Check if participant has admin privileges"""
        return self.role in [ParticipantRole.ADMIN, ParticipantRole.OWNER]

    @property
    def is_owner(self) -> bool:
        """Check if participant is the conversation owner"""
        return self.role == ParticipantRole.OWNER

    @property
    def can_moderate(self) -> bool:
        """Check if participant can perform moderation actions"""
        return self.is_admin and self.is_active

    @property
    def display_name(self) -> str:
        """Get display name for this participant"""
        return self.nickname if self.nickname else "Participant"
