import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.modules.reels.model.reel import ReelStatus, ReelType, ReelVisibility


# Base Schemas
class ReelBase(SQLModel):
    """Base reel schema"""

    type: ReelType = Field(default=ReelType.original)
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    visibility: ReelVisibility = Field(default=ReelVisibility.public)

    # Video details
    video_url: str = Field(min_length=1, max_length=1000)
    thumbnail_url: str = Field(min_length=1, max_length=1000)
    duration: int = Field(ge=15, le=90)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    file_size: int = Field(gt=0)

    # Audio settings
    music_id: Optional[uuid.UUID] = Field(default=None)
    audio_start_time: float = Field(default=0.0, ge=0)
    audio_volume: float = Field(default=1.0, ge=0, le=2)
    is_muted: bool = Field(default=False)

    # Effects and editing
    effects: List[Dict[str, Any]] = Field(default_factory=list)
    text_overlays: List[Dict[str, Any]] = Field(default_factory=list)
    speed_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)

    # Content
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)


class ReelCreate(ReelBase):
    """Schema for creating a new reel"""

    pass


class ReelUpdate(SQLModel):
    """Schema for updating a reel"""

    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    visibility: Optional[ReelVisibility] = Field(default=None)
    hashtags: Optional[List[str]] = Field(default=None)
    mentions: Optional[List[str]] = Field(default=None)


class ReelPublic(ReelBase):
    """Public reel schema with additional fields"""

    id: uuid.UUID
    user_id: uuid.UUID
    status: ReelStatus
    processing_progress: float

    # Engagement metrics
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    save_count: int

    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    # Computed properties
    is_processing: bool
    is_published: bool
    engagement_score: int


class ReelList(SQLModel):
    """Schema for reel list response"""

    data: List[ReelPublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class ReelTrending(SQLModel):
    """Schema for trending reels"""

    reel: ReelPublic
    trending_score: float
    rank: int


class ReelDuetCreate(SQLModel):
    """Schema for creating a duet reel"""

    original_reel_id: uuid.UUID
    video_url: str = Field(min_length=1, max_length=1000)
    thumbnail_url: str = Field(min_length=1, max_length=1000)
    duration: int = Field(ge=15, le=90)
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class ReelStitchCreate(SQLModel):
    """Schema for creating a stitch reel"""

    original_reel_id: uuid.UUID
    start_time: float = Field(ge=0)
    end_time: float = Field(gt=0)
    video_url: str = Field(min_length=1, max_length=1000)
    thumbnail_url: str = Field(min_length=1, max_length=1000)
    duration: int = Field(ge=15, le=90)
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
