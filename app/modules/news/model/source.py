import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import TEXT, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.news.model.news import News


class NewsSource(SQLModel, table=True):
    """News sources (publications, websites, etc.)"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Basic Information
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
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
    political_leaning: Optional[str] = Field(
        default=None, max_length=50
    )  # left, center, right
    bias_rating: Optional[str] = Field(
        default=None, max_length=50
    )  # left_bias, right_bias, mixed
    factual_reporting: Optional[str] = Field(
        default=None, max_length=50
    )  # very_high, high, mixed, low, very_low

    # Source Type
    source_type: str = Field(
        default="online", max_length=50
    )  # online, print, tv, radio, agency
    media_type: str = Field(default="news", max_length=50)  # news, blog, social, agency

    # Verification Status
    is_verified: bool = Field(default=False)
    verification_method: Optional[str] = Field(default=None, max_length=100)
    verified_at: Optional[datetime] = Field(default=None)
    verified_by: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")

    # Content Guidelines
    content_policies: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    editorial_standards: Optional[str] = Field(default=None, sa_column=Column(TEXT))

    # Traffic & Metrics
    monthly_visitors: Optional[int] = Field(default=None)
    social_media_followers: Optional[int] = Field(default=None)

    # API Access
    api_endpoint: Optional[str] = Field(default=None, max_length=500)
    api_key_required: bool = Field(default=False)
    api_rate_limit: Optional[int] = Field(default=None)

    # Status
    is_active: bool = Field(default=True)
    is_publisher: bool = Field(default=False)  # Can publish original content
    is_aggregator: bool = Field(default=False)  # Aggregates from other sources

    # Metrics
    news_count: int = Field(default=0)
    fact_check_count: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_scraped_at: Optional[datetime] = Field(default=None)

    # Relationships
    news: List["News"] = Relationship(back_populates="source")

    class Config:
        orm_mode = True

    def increment_news_count(self) -> None:
        """Increment news count"""
        self.news_count += 1

    def decrement_news_count(self) -> None:
        """Decrement news count"""
        if self.news_count > 0:
            self.news_count -= 1

    def increment_fact_check_count(self) -> None:
        """Increment fact check count"""
        self.fact_check_count += 1

    def get_credibility_rating(self) -> str:
        """Get credibility rating based on score"""
        if self.credibility_score is None:
            return "unknown"
        elif self.credibility_score >= 0.9:
            return "very_high"
        elif self.credibility_score >= 0.8:
            return "high"
        elif self.credibility_score >= 0.6:
            return "mixed"
        elif self.credibility_score >= 0.4:
            return "low"
        else:
            return "very_low"


class NewsSourceFollow(SQLModel, table=True):
    """Users following news sources"""

    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    source_id: uuid.UUID = Field(foreign_key="newssource.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
