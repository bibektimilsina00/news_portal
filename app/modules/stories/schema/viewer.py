import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel


# Base Schemas
class StoryViewerBase(SQLModel):
    """Base story viewer schema"""

    view_duration: Optional[int] = Field(default=None, gt=0)  # seconds watched
    device_type: Optional[str] = Field(
        default=None, max_length=50
    )  # mobile, desktop, etc.


class StoryViewerCreate(StoryViewerBase):
    """Schema for creating a new story viewer record"""

    story_id: uuid.UUID


class StoryViewerUpdate(SQLModel):
    """Schema for updating an existing story viewer record"""

    view_duration: Optional[int] = Field(default=None, gt=0)


class StoryViewerPublic(StoryViewerBase):
    """Public story viewer schema"""

    id: uuid.UUID
    story_id: uuid.UUID
    user_id: uuid.UUID
    viewed_at: datetime


class StoryViewerWithUser(StoryViewerPublic):
    """Story viewer with user information"""

    # user: UserPublic  # TODO: Add when user schemas are available
    pass


class StoryViewerList(SQLModel):
    """Schema for story viewer list responses"""

    viewers: List[StoryViewerPublic]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class StoryViewAnalytics(SQLModel):
    """Analytics for story views"""

    total_views: int
    unique_viewers: int
    average_view_duration: float
    device_breakdown: dict  # device_type -> count
    view_trends: List[dict]  # time-based view data
