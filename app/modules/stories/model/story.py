import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

from app.shared.enums import StoryStatus, StoryType, StoryVisibility

if TYPE_CHECKING:
    from app.modules.stories.model.highlight import StoryHighlight
    from app.modules.stories.model.interaction import StoryInteraction
    from app.modules.stories.model.viewer import StoryViewer
    from app.modules.users.model.user import User


class Story(SQLModel, table=True):
    """Instagram-style Stories model"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Content Fields
    type: StoryType = Field(default=StoryType.photo)
    media_url: str = Field(max_length=1000)  # URL to photo/video
    thumbnail_url: Optional[str] = Field(default=None, max_length=1000)

    # Text overlay
    text_content: Optional[str] = Field(default=None, max_length=1000)
    text_position_x: Optional[float] = Field(default=None)  # 0-1 percentage
    text_position_y: Optional[float] = Field(default=None)  # 0-1 percentage
    text_color: Optional[str] = Field(default="#FFFFFF", max_length=7)  # Hex color
    text_font_size: Optional[int] = Field(default=24, ge=12, le=72)

    # Media metadata
    duration: Optional[int] = Field(default=5, ge=1, le=15)  # seconds for video
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    file_size: Optional[int] = Field(default=None)  # bytes

    # Interactive elements
    interactive_type: Optional[str] = Field(default=None)  # poll, question, quiz
    interactive_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Music integration
    music_id: Optional[uuid.UUID] = Field(default=None, max_length=255)
    music_title: Optional[str] = Field(default=None, max_length=255)
    music_artist: Optional[str] = Field(default=None, max_length=255)
    music_duration: Optional[int] = Field(default=None)  # seconds

    # AR Filters and effects
    filter_name: Optional[str] = Field(default=None, max_length=100)
    effect_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Story settings
    visibility: StoryVisibility = Field(default=StoryVisibility.public)
    allow_replies: bool = Field(default=True)
    show_viewers: bool = Field(default=True)

    # Location
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    # Status and timing
    status: StoryStatus = Field(default=StoryStatus.active)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=24)
    )
    scheduled_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="stories")
    viewers: List["StoryViewer"] = Relationship(back_populates="story")
    interactions: List["StoryInteraction"] = Relationship(back_populates="story")
    # highlights: List["StoryHighlight"] = Relationship(back_populates="stories")

    # Computed properties
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @property
    def time_remaining(self) -> int:
        """Returns seconds remaining until expiration"""
        if self.is_expired:
            return 0
        return int((self.expires_at - datetime.utcnow()).total_seconds())

    @property
    def viewer_count(self) -> int:
        return len(self.viewers)
