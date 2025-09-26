import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.modules.live_streams.model.stream import (
    StreamQuality,
    StreamStatus,
    StreamVisibility,
)


# Base Schemas
class StreamBase(SQLModel):
    """Base stream schema"""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    visibility: StreamVisibility = Field(default=StreamVisibility.public)

    # Stream settings
    quality: StreamQuality = Field(default=StreamQuality.high)
    is_recorded: bool = Field(default=True)
    is_moderated: bool = Field(default=True)
    allow_comments: bool = Field(default=True)
    allow_reactions: bool = Field(default=True)

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)

    # Monetization
    is_monetized: bool = Field(default=False)
    donation_goal: Optional[float] = Field(default=None, ge=0)

    # Content
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(default=None, max_length=100)


class StreamCreate(StreamBase):
    """Schema for creating a new stream"""

    pass


class StreamUpdate(SQLModel):
    """Schema for updating a stream"""

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    visibility: Optional[StreamVisibility] = Field(default=None)
    quality: Optional[StreamQuality] = Field(default=None)
    is_recorded: Optional[bool] = Field(default=None)
    is_moderated: Optional[bool] = Field(default=None)
    allow_comments: Optional[bool] = Field(default=None)
    allow_reactions: Optional[bool] = Field(default=None)
    scheduled_at: Optional[datetime] = Field(default=None)
    is_monetized: Optional[bool] = Field(default=None)
    donation_goal: Optional[float] = Field(default=None, ge=0)
    tags: Optional[List[str]] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=100)


class StreamPublic(StreamBase):
    """Public stream schema with additional fields"""

    id: uuid.UUID
    user_id: uuid.UUID
    status: StreamStatus
    stream_key: str
    playback_url: Optional[str]
    thumbnail_url: Optional[str]

    # Timing
    started_at: Optional[datetime]
    ended_at: Optional[datetime]

    # Analytics
    peak_viewers: int
    total_viewers: int
    total_comments: int
    total_reactions: int
    total_badges: int
    current_viewers: int

    # Monetization
    total_donations: float

    # Recording
    recording_url: Optional[str]
    recording_duration: Optional[int]

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_live: bool
    is_scheduled: bool
    duration: Optional[int]


class StreamList(SQLModel):
    """Schema for stream list response"""

    data: List[StreamPublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class StreamStart(SQLModel):
    """Schema for starting a stream"""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class StreamEnd(SQLModel):
    """Schema for ending a stream"""

    save_recording: bool = Field(default=True)


class StreamAnalytics(SQLModel):
    """Schema for stream analytics"""

    stream_id: uuid.UUID
    total_viewers: int
    peak_viewers: int
    average_viewers: float
    total_duration: int
    total_comments: int
    total_reactions: int
    total_badges: int
    total_donations: float
    viewer_retention: Dict[str, Any]  # Time-based retention data
    geographic_data: Dict[str, int]  # Country-based viewer distribution
