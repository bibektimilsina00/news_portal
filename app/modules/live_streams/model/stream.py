import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class StreamStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"
    CANCELLED = "cancelled"
    PROCESSING = "processing"


class StreamVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class StreamQuality(str, enum.Enum):
    LOW = "480p"
    MEDIUM = "720p"
    HIGH = "1080p"
    ULTRA = "4k"


class Stream(SQLModel, table=True):
    """Live stream model"""

    __tablename__ = "live_streams"

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Stream metadata
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    visibility: StreamVisibility = Field(default=StreamVisibility.PUBLIC)

    # Stream configuration
    stream_key: str = Field(max_length=100, unique=True, index=True)
    playback_url: Optional[str] = Field(default=None, max_length=1000)
    thumbnail_url: Optional[str] = Field(default=None, max_length=1000)

    # Stream settings
    quality: StreamQuality = Field(default=StreamQuality.HIGH)
    is_recorded: bool = Field(default=True)
    is_moderated: bool = Field(default=True)
    allow_comments: bool = Field(default=True)
    allow_reactions: bool = Field(default=True)

    # Stream status and timing
    status: StreamStatus = Field(default=StreamStatus.SCHEDULED)
    scheduled_at: Optional[datetime] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)

    # Stream analytics
    peak_viewers: int = Field(default=0, ge=0)
    current_viewers: int = Field(default=0, ge=0)
    total_viewers: int = Field(default=0, ge=0)
    total_comments: int = Field(default=0, ge=0)
    total_reactions: int = Field(default=0, ge=0)
    total_badges: int = Field(default=0, ge=0)

    # Monetization
    is_monetized: bool = Field(default=False)
    donation_goal: Optional[float] = Field(default=None, ge=0)
    total_donations: float = Field(default=0.0, ge=0)

    # Recording
    recording_url: Optional[str] = Field(default=None, max_length=1000)
    recording_duration: Optional[int] = Field(default=None, ge=0)  # in seconds

    # Stream metadata
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    category: Optional[str] = Field(default=None, max_length=100)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="live_streams")
    # viewers: List["StreamViewer"] = Relationship(back_populates="stream")
    # badges: List["StreamBadge"] = Relationship(back_populates="stream")

    # Computed properties
    @property
    def is_live(self) -> bool:
        """Check if stream is currently live"""
        return self.status == StreamStatus.LIVE

    @property
    def is_scheduled(self) -> bool:
        """Check if stream is scheduled"""
        return self.status == StreamStatus.SCHEDULED

    @property
    def duration(self) -> Optional[int]:
        """Get stream duration in seconds"""
        if self.started_at and self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds())
        elif self.started_at and self.status == StreamStatus.LIVE:
            return int((datetime.utcnow() - self.started_at).total_seconds())
        return None
