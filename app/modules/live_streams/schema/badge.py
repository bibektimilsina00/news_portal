import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.modules.live_streams.model.badge import BadgeType


# Base Schemas
class StreamBadgeBase(SQLModel):
    """Base stream badge schema"""

    badge_type: BadgeType
    amount: float = Field(ge=0)
    message: Optional[str] = Field(default=None, max_length=500)

    # Visual effects
    animation_type: Optional[str] = Field(default=None, max_length=50)
    sound_effect: Optional[str] = Field(default=None, max_length=100)
    display_duration: int = Field(default=5000, ge=1000, le=30000)  # milliseconds

    # Timing
    sent_at: datetime


class StreamBadgeCreate(StreamBadgeBase):
    """Schema for creating a stream badge"""

    stream_id: uuid.UUID
    sender_id: uuid.UUID


class StreamBadgeUpdate(SQLModel):
    """Schema for updating a stream badge"""

    message: Optional[str] = Field(default=None, max_length=500)
    animation_type: Optional[str] = Field(default=None, max_length=50)
    sound_effect: Optional[str] = Field(default=None, max_length=100)
    display_duration: Optional[int] = Field(default=None, ge=1000, le=30000)


class StreamBadgePublic(StreamBadgeBase):
    """Public stream badge schema"""

    id: uuid.UUID
    stream_id: uuid.UUID
    sender_id: uuid.UUID

    # Computed properties
    is_donation: bool

    # Timestamps
    created_at: datetime
    updated_at: datetime


class StreamBadgeList(SQLModel):
    """Schema for badge list response"""

    data: List[StreamBadgePublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class BadgeTemplate(SQLModel):
    """Schema for badge templates"""

    badge_type: BadgeType
    name: str = Field(max_length=50)
    description: str = Field(max_length=200)
    default_amount: float = Field(ge=0)
    min_amount: float = Field(ge=0)
    max_amount: Optional[float] = Field(default=None, ge=0)
    animation_type: Optional[str] = Field(default=None, max_length=50)
    sound_effect: Optional[str] = Field(default=None, max_length=100)
    display_duration: int = Field(default=5000, ge=1000, le=30000)
    is_active: bool = Field(default=True)


class StreamBadgeStats(SQLModel):
    """Schema for stream badge statistics"""

    stream_id: uuid.UUID
    total_badges: int
    total_amount: float
    average_amount: float
    top_badge_type: BadgeType
    badge_type_breakdown: dict  # {"heart": 50, "star": 30, "diamond": 20}
    hourly_distribution: List[dict]  # [{"hour": 14, "count": 10, "amount": 50.0}]
