import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.modules.live_streams.model.viewer import ViewerRole


# Base Schemas
class StreamViewerBase(SQLModel):
    """Base stream viewer schema"""

    role: ViewerRole = Field(default=ViewerRole.viewer)
    is_muted: bool = Field(default=False)
    is_banned: bool = Field(default=False)

    # Engagement metrics
    comments_count: int = Field(default=0, ge=0)
    reactions_count: int = Field(default=0, ge=0)
    badges_count: int = Field(default=0, ge=0)

    # Session info
    joined_at: datetime
    left_at: Optional[datetime] = Field(default=None)

    # Device info
    device_type: Optional[str] = Field(default=None, max_length=50)
    browser: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=100)


class StreamViewerCreate(StreamViewerBase):
    """Schema for creating a stream viewer"""

    stream_id: uuid.UUID
    user_id: uuid.UUID


class StreamViewerUpdate(SQLModel):
    """Schema for updating a stream viewer"""

    role: Optional[ViewerRole] = Field(default=None)
    is_muted: Optional[bool] = Field(default=None)
    is_banned: Optional[bool] = Field(default=None)


class StreamViewerPublic(StreamViewerBase):
    """Public stream viewer schema"""

    id: uuid.UUID
    stream_id: uuid.UUID
    user_id: uuid.UUID

    # Computed properties
    session_duration: Optional[int]  # in seconds
    total_engagement: int  # sum of comments, reactions, badges

    # Timestamps
    created_at: datetime
    updated_at: datetime


class StreamViewerList(SQLModel):
    """Schema for viewer list response"""

    data: List[StreamViewerPublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class ViewerEngagement(SQLModel):
    """Schema for viewer engagement data"""

    viewer_id: uuid.UUID
    stream_id: uuid.UUID
    engagement_type: str  # comment, reaction, badge
    timestamp: datetime
    extra_data: Optional[dict] = Field(
        default=None
    )  # Additional data like reaction type, badge amount


class StreamViewerStats(SQLModel):
    """Schema for stream viewer statistics"""

    stream_id: uuid.UUID
    total_viewers: int
    unique_viewers: int
    average_session_duration: float
    peak_concurrent_viewers: int
    viewer_retention_rate: float  # percentage
    top_countries: List[dict]  # [{"country": "US", "count": 100}]
    device_breakdown: dict  # {"mobile": 50, "desktop": 30, "tablet": 20}
