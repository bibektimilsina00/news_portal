import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.news.model.category import Category
    from app.modules.news.model.factcheck import FactCheck
    from app.modules.news.model.source import NewsSource
    from app.modules.users.model.user import User


class NewsStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"


class NewsPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    BREAKING = "breaking"


class News(SQLModel, table=True):
    """News articles model"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    category_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="category.id", index=True
    )
    source_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="newssource.id", index=True
    )

    # Content Fields
    title: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
    content: str
    summary: Optional[str] = Field(default=None)
    excerpt: Optional[str] = Field(default=None, max_length=500)

    # Media Fields
    featured_image_url: Optional[str] = Field(default=None, max_length=500)
    video_url: Optional[str] = Field(default=None, max_length=500)
    gallery_images: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # News Metadata
    headline: Optional[str] = Field(default=None, max_length=255)
    subheadline: Optional[str] = Field(default=None, max_length=255)
    lead_text: Optional[str] = Field(default=None, max_length=1000)

    # Location & Geography
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    country: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # News Specific Fields
    is_breaking_news: bool = Field(default=False, index=True)
    is_featured: bool = Field(default=False, index=True)
    is_trending: bool = Field(default=False, index=True)
    priority: NewsPriority = Field(default=NewsPriority.MEDIUM, index=True)

    # Source & Attribution
    original_url: Optional[str] = Field(default=None, max_length=1000)
    author_name: Optional[str] = Field(default=None, max_length=255)
    author_email: Optional[str] = Field(default=None, max_length=255)
    publication_date: Optional[datetime] = Field(default=None)

    # Fact Checking
    fact_check_status: str = Field(default="pending", max_length=50, index=True)
    fact_check_summary: Optional[str] = Field(default=None)
    credibility_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # SEO & Metadata
    meta_title: Optional[str] = Field(default=None, max_length=255)
    meta_description: Optional[str] = Field(default=None, max_length=500)
    meta_keywords: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    canonical_url: Optional[str] = Field(default=None, max_length=1000)

    # Status & Visibility
    status: NewsStatus = Field(default=NewsStatus.DRAFT, index=True)
    visibility: str = Field(
        default="public", max_length=50
    )  # public, followers_only, private

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None, index=True)
    published_at: Optional[datetime] = Field(default=None, index=True)
    archived_at: Optional[datetime] = Field(default=None)

    # Engagement Metrics
    view_count: int = Field(default=0)
    like_count: int = Field(default=0)
    comment_count: int = Field(default=0)
    share_count: int = Field(default=0)
    bookmark_count: int = Field(default=0)

    # Social Metrics
    facebook_shares: int = Field(default=0)
    twitter_shares: int = Field(default=0)
    linkedin_shares: int = Field(default=0)
    whatsapp_shares: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    last_interaction_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    author: "User" = Relationship(back_populates="news")
    category: Optional["Category"] = Relationship(back_populates="news")
    source: Optional["NewsSource"] = Relationship(back_populates="news")
    fact_checks: List["FactCheck"] = Relationship(back_populates="news")

    class Config:
        orm_mode = True

    def increment_view_count(self) -> None:
        """Increment view count"""
        self.view_count += 1
        self.last_interaction_at = datetime.utcnow()

    def increment_like_count(self) -> None:
        """Increment like count"""
        self.like_count += 1
        self.last_interaction_at = datetime.utcnow()

    def decrement_like_count(self) -> None:
        """Decrement like count"""
        if self.like_count > 0:
            self.like_count -= 1
            self.last_interaction_at = datetime.utcnow()

    def increment_comment_count(self) -> None:
        """Increment comment count"""
        self.comment_count += 1
        self.last_interaction_at = datetime.utcnow()

    def decrement_comment_count(self) -> None:
        """Decrement comment count"""
        if self.comment_count > 0:
            self.comment_count -= 1
            self.last_interaction_at = datetime.utcnow()

    def increment_share_count(self) -> None:
        """Increment share count"""
        self.share_count += 1
        self.last_interaction_at = datetime.utcnow()

    def increment_bookmark_count(self) -> None:
        """Increment bookmark count"""
        self.bookmark_count += 1
        self.last_interaction_at = datetime.utcnow()

    def decrement_bookmark_count(self) -> None:
        """Decrement bookmark count"""
        if self.bookmark_count > 0:
            self.bookmark_count -= 1
            self.last_interaction_at = datetime.utcnow()

    def is_published(self) -> bool:
        """Check if news is published"""
        return self.status == NewsStatus.PUBLISHED and self.published_at is not None

    def is_scheduled(self) -> bool:
        """Check if news is scheduled"""
        return self.status == NewsStatus.SCHEDULED and self.scheduled_at is not None

    def is_breaking(self) -> bool:
        """Check if news is breaking news"""
        return self.is_breaking_news

    def get_reading_time(self) -> int:
        """Calculate estimated reading time in minutes"""
        # Average reading speed: 200 words per minute
        word_count = len(self.content.split())
        reading_time = word_count / 200
        return max(1, int(reading_time))

    def get_share_url(self) -> str:
        """Generate share URL"""
        if self.slug:
            return f"{settings.FRONTEND_URL}/news/{self.slug}"
        return f"{settings.FRONTEND_URL}/news/{self.id}"


class NewsTag(SQLModel, table=True):
    """Many-to-many relationship between news and tags"""

    news_id: uuid.UUID = Field(foreign_key="news.id", primary_key=True)
    id: uuid.UUID = Field(foreign_key="newstag.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class NewsRelated(SQLModel, table=True):
    """Related news articles"""

    news_id: uuid.UUID = Field(foreign_key="news.id", primary_key=True)
    related_news_id: uuid.UUID = Field(foreign_key="news.id", primary_key=True)
    relevance_score: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
