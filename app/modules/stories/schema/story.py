import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.modules.stories.model.story import StoryStatus, StoryType, StoryVisibility


# Base Schemas
class StoryBase(SQLModel):
    """Base story schema"""

    type: StoryType = Field(default=StoryType.photo)
    media_url: str = Field(min_length=1, max_length=1000)
    thumbnail_url: Optional[str] = Field(default=None, max_length=1000)

    # Text overlay
    text_content: Optional[str] = Field(default=None, max_length=1000)
    text_position_x: Optional[float] = Field(default=None, ge=0, le=1)
    text_position_y: Optional[float] = Field(default=None, ge=0, le=1)
    text_color: Optional[str] = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    text_font_size: Optional[int] = Field(default=24, ge=12, le=72)

    # Media metadata
    duration: Optional[int] = Field(default=5, ge=1, le=15)
    width: Optional[int] = Field(default=None, gt=0)
    height: Optional[int] = Field(default=None, gt=0)
    file_size: Optional[int] = Field(default=None, gt=0)

    # Interactive elements
    interactive_type: Optional[str] = Field(default=None)
    interactive_data: Optional[Dict[str, Any]] = Field(default=None)

    # Music integration
    music_id: Optional[str] = Field(default=None, max_length=255)
    music_title: Optional[str] = Field(default=None, max_length=255)
    music_artist: Optional[str] = Field(default=None, max_length=255)
    music_duration: Optional[int] = Field(default=None, gt=0)

    # AR Filters and effects
    filter_name: Optional[str] = Field(default=None, max_length=100)
    effect_data: Optional[Dict[str, Any]] = Field(default=None)

    # Story settings
    visibility: StoryVisibility = Field(default=StoryVisibility.public)
    allow_replies: bool = Field(default=True)
    show_viewers: bool = Field(default=True)

    # Location
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)


class StoryCreate(StoryBase):
    """Schema for creating a new story"""

    pass


class StoryUpdate(SQLModel):
    """Schema for updating an existing story"""

    # Content updates
    text_content: Optional[str] = Field(default=None, max_length=1000)
    text_position_x: Optional[float] = Field(default=None, ge=0, le=1)
    text_position_y: Optional[float] = Field(default=None, ge=0, le=1)
    text_color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    text_font_size: Optional[int] = Field(default=None, ge=12, le=72)

    # Interactive elements
    interactive_type: Optional[str] = Field(default=None)
    interactive_data: Optional[Dict[str, Any]] = Field(default=None)

    # Music
    music_id: Optional[str] = Field(default=None, max_length=255)
    music_title: Optional[str] = Field(default=None, max_length=255)
    music_artist: Optional[str] = Field(default=None, max_length=255)
    music_duration: Optional[int] = Field(default=None, gt=0)

    # Effects
    filter_name: Optional[str] = Field(default=None, max_length=100)
    effect_data: Optional[Dict[str, Any]] = Field(default=None)

    # Settings
    visibility: Optional[StoryVisibility] = Field(default=None)
    allow_replies: Optional[bool] = Field(default=None)
    show_viewers: Optional[bool] = Field(default=None)

    # Location
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)


class StoryPublic(StoryBase):
    """Public story schema with additional computed fields"""

    id: uuid.UUID
    user_id: uuid.UUID
    status: StoryStatus
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_expired: bool
    time_remaining: int
    viewer_count: int


class StoryWithUser(StoryPublic):
    """Story with user information"""

    # User information would be added here
    # user: UserPublic  # TODO: Add when user schemas are available
    pass


class StoryList(SQLModel):
    """Schema for story list responses"""

    stories: List[StoryPublic]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


# Interactive element schemas
class PollData(BaseModel):
    """Schema for poll interactive data"""

    question: str = Field(min_length=1, max_length=200)
    options: List[str] = Field(default_factory=list)  # 2-4 options
    allow_multiple: bool = Field(default=False)


class QuestionData(BaseModel):
    """Schema for question interactive data"""

    question: str = Field(min_length=1, max_length=200)
    placeholder: Optional[str] = Field(default="Your answer...", max_length=100)


class QuizData(BaseModel):
    """Schema for quiz interactive data"""

    question: str = Field(min_length=1, max_length=200)
    options: List[str] = Field(default_factory=list)  # 2-4 options
    correct_option: int = Field(ge=0)  # Index of correct option
    explanation: Optional[str] = Field(default=None, max_length=500)
