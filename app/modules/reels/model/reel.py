import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

from app.shared.enums import ReelStatus, ReelType, ReelVisibility

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class Reel(SQLModel, table=True):
    """Reel video content model"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    music_id: Optional[uuid.UUID] = Field(default=None, foreign_key="music.id")
    duet_reel_id: Optional[uuid.UUID] = Field(default=None, foreign_key="reel.id")
    stitch_reel_id: Optional[uuid.UUID] = Field(default=None, foreign_key="reel.id")

    # Reel metadata
    type: ReelType = Field(default=ReelType.ORIGINAL)
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    visibility: ReelVisibility = Field(default=ReelVisibility.PUBLIC)

    # Video details
    video_url: str = Field(max_length=1000)
    thumbnail_url: str = Field(max_length=1000)
    duration: int = Field(ge=15, le=90)  # 15-90 seconds
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    file_size: int = Field(gt=0)

    # Audio settings
    audio_start_time: float = Field(default=0.0, ge=0)
    audio_volume: float = Field(default=1.0, ge=0, le=2)
    is_muted: bool = Field(default=False)

    # Effects and editing
    effects: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    text_overlays: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    speed_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)

    # Engagement metrics
    view_count: int = Field(default=0, ge=0)
    like_count: int = Field(default=0, ge=0)
    comment_count: int = Field(default=0, ge=0)
    share_count: int = Field(default=0, ge=0)
    save_count: int = Field(default=0, ge=0)

    # Hashtags and mentions
    hashtags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    mentions: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Processing status
    status: ReelStatus = Field(default=ReelStatus.PROCESSING)
    processing_progress: float = Field(default=0.0, ge=0, le=100)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="reels")

    # Computed properties
    @property
    def is_processing(self) -> bool:
        return self.status == ReelStatus.PROCESSING

    @property
    def is_published(self) -> bool:
        return self.status == ReelStatus.PUBLISHED

    @property
    def engagement_score(self) -> int:
        """Calculate engagement score based on likes, comments, shares, saves"""
        return (
            self.like_count
            + (self.comment_count * 2)
            + (self.share_count * 3)
            + (self.save_count * 2)
        )
