import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from sqlmodel import SQLModel

from app.modules.posts.model.post import PostStatus, PostType, PostVisibility


# Base Schemas
class PostBase(SQLModel):
    """Base post schema"""

    caption: Optional[str] = Field(default=None, max_length=2200)
    content: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None, max_length=500)

    # Post type & visibility
    post_type: PostType = Field(default=PostType.regular)
    visibility: PostVisibility = Field(default=PostVisibility.public)

    # Media
    media_urls: Optional[List[str]] = Field(default=[])
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)

    # Location
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # Flags
    is_sensitive: bool = Field(default=False)
    is_highlighted: bool = Field(default=False)
    is_pinned: bool = Field(default=False)
    is_breaking_news: bool = Field(default=False)

    # Fact checking
    fact_check_status: Optional[str] = Field(default="pending", max_length=50)

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)

    @validator("media_urls")
    def validate_media_urls(cls, v):
        if v:
            for url in v:
                if url and not url.startswith(("http://", "https://")):
                    raise ValueError(f"Invalid URL: {url}")
        return v

    @validator("thumbnail_url", "cover_image_url")
    def validate_image_urls(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Image URL must start with http:// or https://")
        return v


class PostCreate(PostBase):
    """Create post schema"""

    user_id: uuid.UUID


class PostUpdate(BaseModel):
    """Update post schema"""

    caption: Optional[str] = Field(default=None, max_length=2200)
    content: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None, max_length=500)

    # Media
    media_urls: Optional[List[str]] = Field(default=None)
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)

    # Location
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # Flags
    is_sensitive: Optional[bool] = Field(default=None)
    is_highlighted: Optional[bool] = Field(default=None)
    is_pinned: Optional[bool] = Field(default=None)
    is_breaking_news: Optional[bool] = Field(default=None)

    # Status & visibility
    status: Optional[PostStatus] = Field(default=None)
    visibility: Optional[PostVisibility] = Field(default=None)

    # Fact checking
    fact_check_status: Optional[str] = Field(default=None, max_length=50)

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)


class PostResponse(PostBase):
    """Post response schema"""

    id: uuid.UUID
    user_id: uuid.UUID
    status: PostStatus
    published_at: Optional[datetime]

    # Engagement metrics
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    bookmark_count: int = 0
    view_count: int = 0

    # Social metrics
    facebook_shares: int = 0
    twitter_shares: int = 0
    linkedin_shares: int = 0
    whatsapp_shares: int = 0

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    last_interaction_at: Optional[datetime]

    # Computed fields
    share_url: Optional[str] = Field(default=None)
    is_published: Optional[bool] = Field(default=None)

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """Post list response"""

    posts: List[PostResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class PostFilter(BaseModel):
    """Post filter schema"""

    # Content filters
    user_id: Optional[uuid.UUID] = None
    post_type: Optional[PostType] = None
    status: Optional[PostStatus] = None
    visibility: Optional[PostVisibility] = None

    # Media filters
    has_media: Optional[bool] = None
    has_location: Optional[bool] = None
    is_sensitive: Optional[bool] = None
    is_highlighted: Optional[bool] = None
    is_pinned: Optional[bool] = None
    is_breaking_news: Optional[bool] = None

    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None

    # Location filters
    country: Optional[str] = None
    city: Optional[str] = None

    # Search
    search_query: Optional[str] = None

    # Sorting
    sort_by: Optional[str] = Field(
        default="created_at",
        pattern="^(created_at|published_at|like_count|comment_count|view_count)$",
    )
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


class PostStats(BaseModel):
    """Post statistics"""

    total_posts: int
    published_posts: int
    draft_posts: int
    scheduled_posts: int
    posts_with_media: int
    posts_with_location: int


class PostPublishRequest(BaseModel):
    """Post publish request"""

    post_id: uuid.UUID
    scheduled_at: Optional[datetime] = None


class PostPublishResponse(BaseModel):
    """Post publish response"""

    post_id: uuid.UUID
    status: PostStatus
    published_at: Optional[datetime]
    message: str


class PostScheduleRequest(BaseModel):
    """Post schedule request"""

    post_id: uuid.UUID
    scheduled_at: datetime


class PostSearchResponse(BaseModel):
    """Post search response"""

    results: List[PostResponse]
    total: int
    query: str
    suggestions: List[str] = []


class PostByLocationResponse(BaseModel):
    """Post by location response"""

    location: str
    posts: List[PostResponse]
    total: int
    coordinates: Optional[Dict[str, float]] = None


class PostEngagementResponse(BaseModel):
    """Post engagement response"""

    post_id: uuid.UUID
    like_count: int
    comment_count: int
    share_count: int
    bookmark_count: int
    view_count: int
    engagement_rate: float


class PostMediaItem(BaseModel):
    """Post media item"""

    media_type: str
    media_url: str
    thumbnail_url: Optional[str] = None
    sort_order: int = 0
    alt_text: Optional[str] = None
    caption: Optional[str] = None


class PostWithMediaCreate(BaseModel):
    """Create post with media"""

    post_data: PostCreate
    media_items: List[PostMediaItem]


class PostWithMediaResponse(PostResponse):
    """Post with media response"""

    media_items: List[PostMediaItem] = []
