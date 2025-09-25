import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel


# Base Schemas
class StoryHighlightBase(SQLModel):
    """Base story highlight schema"""

    title: str = Field(min_length=1, max_length=100)
    cover_image_url: Optional[str] = Field(default=None, max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    is_private: bool = Field(default=False)
    is_archived: bool = Field(default=False)


class StoryHighlightCreate(StoryHighlightBase):
    """Schema for creating a new story highlight"""

    story_ids: List[uuid.UUID] = Field(default_factory=list)  # Stories to include


class StoryHighlightUpdate(SQLModel):
    """Schema for updating an existing story highlight"""

    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    cover_image_url: Optional[str] = Field(default=None, max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    is_private: Optional[bool] = Field(default=None)
    is_archived: Optional[bool] = Field(default=None)
    story_ids: Optional[List[uuid.UUID]] = Field(default=None)  # Update stories


class StoryHighlightPublic(StoryHighlightBase):
    """Public story highlight schema"""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    story_count: int


class StoryHighlightWithStories(StoryHighlightPublic):
    """Story highlight with story details"""

    # stories: List[StoryPublic]  # TODO: Add when story schemas are available
    pass


class StoryHighlightList(SQLModel):
    """Schema for story highlight list responses"""

    highlights: List[StoryHighlightPublic]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
