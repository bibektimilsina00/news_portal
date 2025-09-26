import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from sqlmodel import SQLModel

from app.modules.news.model.news import NewsPriority, NewsStatus


# Base Schemas
class NewsBase(SQLModel):
    """Base news schema"""

    title: str = Field(min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, max_length=255)
    content: str = Field(min_length=1)
    summary: Optional[str] = Field(default=None)
    excerpt: Optional[str] = Field(default=None, max_length=500)

    # Media
    featured_image_url: Optional[str] = Field(default=None, max_length=500)
    video_url: Optional[str] = Field(default=None, max_length=500)
    gallery_images: Optional[List[str]] = Field(default=[])

    # Metadata
    headline: Optional[str] = Field(default=None, max_length=255)
    subheadline: Optional[str] = Field(default=None, max_length=255)
    lead_text: Optional[str] = Field(default=None, max_length=1000)

    # Location
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    country: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # News flags
    is_breaking_news: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    is_trending: bool = Field(default=False)
    priority: NewsPriority = Field(default=NewsPriority.MEDIUM)

    # Source & Attribution
    original_url: Optional[str] = Field(default=None, max_length=1000)
    author_name: Optional[str] = Field(default=None, max_length=255)
    author_email: Optional[str] = Field(default=None, max_length=255)
    publication_date: Optional[datetime] = Field(default=None)

    # Fact Checking
    fact_check_status: str = Field(default="pending", max_length=50)
    fact_check_summary: Optional[str] = Field(default=None)
    credibility_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # SEO
    meta_title: Optional[str] = Field(default=None, max_length=255)
    meta_description: Optional[str] = Field(default=None, max_length=500)
    meta_keywords: Optional[List[str]] = Field(default=[])
    canonical_url: Optional[str] = Field(default=None, max_length=1000)

    # Status & Visibility
    status: NewsStatus = Field(default=NewsStatus.DRAFT)
    visibility: str = Field(default="public", max_length=50)

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)

    # Validation
    @validator("slug")
    def validate_slug(cls, v):
        if v and not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Slug must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v

    @validator("featured_image_url", "video_url")
    def validate_urls(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class NewsCreate(NewsBase):
    """Create news schema"""

    user_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    source_id: Optional[uuid.UUID] = None


class NewsUpdate(BaseModel):
    """Update news schema"""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = Field(default=None, min_length=1)
    summary: Optional[str] = Field(default=None)
    excerpt: Optional[str] = Field(default=None, max_length=500)

    # Media
    featured_image_url: Optional[str] = Field(default=None, max_length=500)
    video_url: Optional[str] = Field(default=None, max_length=500)
    gallery_images: Optional[List[str]] = Field(default=None)

    # Metadata
    headline: Optional[str] = Field(default=None, max_length=255)
    subheadline: Optional[str] = Field(default=None, max_length=255)
    lead_text: Optional[str] = Field(default=None, max_length=1000)

    # Location
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    country: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # News flags
    is_breaking_news: Optional[bool] = Field(default=None)
    is_featured: Optional[bool] = Field(default=None)
    is_trending: Optional[bool] = Field(default=None)
    priority: Optional[NewsPriority] = Field(default=None)

    # Source & Attribution
    original_url: Optional[str] = Field(default=None, max_length=1000)
    author_name: Optional[str] = Field(default=None, max_length=255)
    author_email: Optional[str] = Field(default=None, max_length=255)
    publication_date: Optional[datetime] = Field(default=None)

    # Fact Checking
    fact_check_status: Optional[str] = Field(default=None, max_length=50)
    fact_check_summary: Optional[str] = Field(default=None)
    credibility_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # SEO
    meta_title: Optional[str] = Field(default=None, max_length=255)
    meta_description: Optional[str] = Field(default=None, max_length=500)
    meta_keywords: Optional[List[str]] = Field(default=None)
    canonical_url: Optional[str] = Field(default=None, max_length=1000)

    # Status & Visibility
    status: Optional[NewsStatus] = Field(default=None)
    visibility: Optional[str] = Field(default=None, max_length=50)

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None)


class NewsResponse(NewsBase):
    """News response schema"""

    id: uuid.UUID
    user_id: uuid.UUID
    category_id: Optional[uuid.UUID]
    source_id: Optional[uuid.UUID]

    # Engagement metrics
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    bookmark_count: int = 0

    # Social metrics
    facebook_shares: int = 0
    twitter_shares: int = 0
    linkedin_shares: int = 0
    whatsapp_shares: int = 0

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    last_interaction_at: Optional[datetime]

    # Computed fields
    reading_time: Optional[int] = Field(default=None)
    share_url: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    """News list response"""

    news: List[NewsResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class NewsFilter(BaseModel):
    """News filter schema"""

    # Content filters
    category_id: Optional[uuid.UUID] = None
    source_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None

    # Status filters
    status: Optional[NewsStatus] = None
    is_breaking_news: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_trending: Optional[bool] = None
    priority: Optional[NewsPriority] = None

    # Location filters
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None

    # Date filters
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

    # Search
    search_query: Optional[str] = None

    # Sorting
    sort_by: Optional[str] = Field(
        default="published_at",
        pattern="^(published_at|created_at|view_count|like_count|comment_count)$",
    )
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


class NewsStats(BaseModel):
    """News statistics"""

    total_news: int
    published_news: int
    draft_news: int
    scheduled_news: int
    breaking_news: int
    featured_news: int
    trending_news: int


class BreakingNewsResponse(BaseModel):
    """Breaking news response"""

    breaking_news: List[NewsResponse]
    total: int
    last_updated: datetime


class TrendingNewsResponse(BaseModel):
    """Trending news response"""

    trending_news: List[NewsResponse]
    total: int
    time_period: str


class NewsPublishRequest(BaseModel):
    """News publish request"""

    news_id: uuid.UUID
    scheduled_at: Optional[datetime] = None


class NewsPublishResponse(BaseModel):
    """News publish response"""

    news_id: uuid.UUID
    status: NewsStatus
    published_at: Optional[datetime]
    message: str


class NewsScheduleRequest(BaseModel):
    """News schedule request"""

    news_id: uuid.UUID
    scheduled_at: datetime


class NewsSearchResponse(BaseModel):
    """News search response"""

    results: List[NewsResponse]
    total: int
    query: str
    suggestions: List[str] = []


class NewsByLocationResponse(BaseModel):
    """News by location response"""

    location: str
    news: List[NewsResponse]
    total: int
    coordinates: Optional[Dict[str, float]] = None
