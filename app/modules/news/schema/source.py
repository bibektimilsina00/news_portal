import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel


# Base Schemas
class NewsSourceBase(SQLModel):
    """Base news source schema"""

    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Contact Information
    website_url: Optional[str] = Field(default=None, max_length=500)
    rss_feed_url: Optional[str] = Field(default=None, max_length=500)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)

    # Location
    country: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    headquarters: Optional[str] = Field(default=None, max_length=255)

    # Media
    logo_url: Optional[str] = Field(default=None, max_length=500)
    favicon_url: Optional[str] = Field(default=None, max_length=500)

    # Credibility & Reliability
    credibility_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fact_checking_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Bias & Political Leaning
    political_leaning: Optional[str] = Field(default=None, max_length=50)
    bias_rating: Optional[str] = Field(default=None, max_length=50)
    factual_reporting: Optional[str] = Field(default=None, max_length=50)

    # Source Type
    source_type: str = Field(default="online", max_length=50)
    media_type: str = Field(default="news", max_length=50)

    # Verification Status
    is_verified: bool = Field(default=False)
    verification_method: Optional[str] = Field(default=None, max_length=100)

    # Content Guidelines
    content_policies: Optional[str] = Field(default=None)
    editorial_standards: Optional[str] = Field(default=None)

    # Traffic & Metrics
    monthly_visitors: Optional[int] = Field(default=None, ge=0)
    social_media_followers: Optional[int] = Field(default=None, ge=0)

    # API Access
    api_endpoint: Optional[str] = Field(default=None, max_length=500)
    api_key_required: bool = Field(default=False)
    api_rate_limit: Optional[int] = Field(default=None, ge=0)

    # Status
    is_active: bool = Field(default=True)
    is_publisher: bool = Field(default=False)
    is_aggregator: bool = Field(default=False)


# Public Schemas
class NewsSourcePublic(NewsSourceBase):
    """Public news source schema"""

    id: uuid.UUID
    news_count: int
    fact_check_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_scraped_at: Optional[datetime]
    verified_at: Optional[datetime]


# Create Schemas
class NewsSourceCreate(NewsSourceBase):
    """News source creation schema"""

    pass


# Update Schemas
class NewsSourceUpdate(BaseModel):
    """News source update schema"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    website_url: Optional[str] = Field(default=None, max_length=500)
    rss_feed_url: Optional[str] = Field(default=None, max_length=500)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    country: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    headquarters: Optional[str] = Field(default=None, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    favicon_url: Optional[str] = Field(default=None, max_length=500)
    credibility_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fact_checking_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    political_leaning: Optional[str] = Field(default=None, max_length=50)
    bias_rating: Optional[str] = Field(default=None, max_length=50)
    factual_reporting: Optional[str] = Field(default=None, max_length=50)
    source_type: Optional[str] = Field(default=None, max_length=50)
    media_type: Optional[str] = Field(default=None, max_length=50)
    is_verified: Optional[bool] = Field(default=None)
    verification_method: Optional[str] = Field(default=None, max_length=100)
    content_policies: Optional[str] = Field(default=None)
    editorial_standards: Optional[str] = Field(default=None)
    monthly_visitors: Optional[int] = Field(default=None, ge=0)
    social_media_followers: Optional[int] = Field(default=None, ge=0)
    api_endpoint: Optional[str] = Field(default=None, max_length=500)
    api_key_required: Optional[bool] = Field(default=None)
    api_rate_limit: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = Field(default=None)
    is_publisher: Optional[bool] = Field(default=None)
    is_aggregator: Optional[bool] = Field(default=None)


# Response Schemas
class NewsSourcesList(BaseModel):
    """List of news sources response"""

    data: List[NewsSourcePublic]
    total: int
    page: int = 1
    per_page: int = 50


class NewsSourceStats(BaseModel):
    """News source statistics"""

    total_sources: int
    active_sources: int
    verified_sources: int
    total_news: int
    average_credibility: float


# News Source Follow Schemas
class NewsSourceFollowBase(SQLModel):
    """Base news source follow schema"""

    user_id: uuid.UUID
    source_id: uuid.UUID


class NewsSourceFollowPublic(NewsSourceFollowBase):
    """Public news source follow schema"""

    created_at: datetime


class NewsSourceFollowCreate(NewsSourceFollowBase):
    """News source follow creation schema"""

    pass


class NewsSourceFollowsList(BaseModel):
    """List of news source follows response"""

    data: List[NewsSourceFollowPublic]
    total: int
