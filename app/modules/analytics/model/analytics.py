import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class UserAnalytics(SQLModel, table=True):
    """User analytics tracking model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # User reference
    user_id: uuid.UUID = Field(index=True)

    # Profile analytics
    profile_views: int = Field(default=0)
    follower_count: int = Field(default=0)
    following_count: int = Field(default=0)

    # Engagement metrics
    total_posts: int = Field(default=0)
    total_likes_received: int = Field(default=0)
    total_comments_received: int = Field(default=0)
    total_shares_received: int = Field(default=0)
    total_bookmarks_received: int = Field(default=0)

    # Content performance
    avg_engagement_rate: float = Field(default=0.0)
    top_performing_post_id: Optional[uuid.UUID] = Field(default=None)
    top_performing_score: float = Field(default=0.0)

    # Activity tracking
    login_count: int = Field(default=0)
    last_login_at: Optional[datetime] = Field(default=None)
    session_duration_avg: int = Field(default=0)  # in seconds

    # Demographics (aggregated)
    audience_locations: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    audience_age_groups: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    audience_genders: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Revenue analytics (if monetization enabled)
    total_earnings: float = Field(default=0.0)
    subscription_count: int = Field(default=0)

    # Time tracking
    date_recorded: datetime = Field(default_factory=datetime.utcnow, index=True)
    week_start: datetime = Field(
        index=True
    )  # Start of the week for weekly aggregations
    month_start: datetime = Field(
        index=True
    )  # Start of the month for monthly aggregations

    # Metadata
    metadata_: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class ContentAnalytics(SQLModel, table=True):
    """Content analytics tracking model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Content reference
    content_id: uuid.UUID = Field(
        index=True
    )  # Could be post_id, story_id, reel_id, etc.
    content_type: str = Field(
        index=True
    )  # "post", "story", "reel", "news", "live_stream"

    # User reference
    author_id: uuid.UUID = Field(index=True)

    # Basic metrics
    views: int = Field(default=0)
    likes: int = Field(default=0)
    comments: int = Field(default=0)
    shares: int = Field(default=0)
    bookmarks: int = Field(default=0)

    # Engagement metrics
    engagement_rate: float = Field(default=0.0)  # (likes + comments + shares) / views
    click_through_rate: float = Field(default=0.0)
    average_view_duration: int = Field(default=0)  # in seconds

    # Content-specific metrics
    video_completion_rate: Optional[float] = Field(default=None)  # For videos
    story_completion_rate: Optional[float] = Field(default=None)  # For stories
    live_viewer_peak: Optional[int] = Field(default=None)  # For live streams
    live_duration: Optional[int] = Field(default=None)  # For live streams in seconds

    # Geographic data
    viewer_locations: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Device and platform data
    device_types: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    platforms: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Time-based data
    hourly_views: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    daily_views: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Performance score
    performance_score: float = Field(default=0.0)  # Calculated score for ranking

    # Time tracking
    date_recorded: datetime = Field(default_factory=datetime.utcnow, index=True)
    content_created_at: datetime = Field(index=True)

    # Metadata
    metadata_: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class PlatformAnalytics(SQLModel, table=True):
    """Platform-wide analytics model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Platform metrics
    total_users: int = Field(default=0)
    active_users_daily: int = Field(default=0)
    active_users_weekly: int = Field(default=0)
    active_users_monthly: int = Field(default=0)

    # Content metrics
    total_posts: int = Field(default=0)
    total_stories: int = Field(default=0)
    total_reels: int = Field(default=0)
    total_news_articles: int = Field(default=0)
    total_live_streams: int = Field(default=0)

    # Engagement metrics
    total_likes: int = Field(default=0)
    total_comments: int = Field(default=0)
    total_shares: int = Field(default=0)
    total_bookmarks: int = Field(default=0)

    # Geographic distribution
    top_countries: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    top_cities: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Device and platform stats
    device_breakdown: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    platform_breakdown: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Revenue metrics (if applicable)
    total_revenue: float = Field(default=0.0)
    subscription_revenue: float = Field(default=0.0)
    ad_revenue: float = Field(default=0.0)

    # Time tracking
    date_recorded: datetime = Field(default_factory=datetime.utcnow, index=True)
    week_start: datetime = Field(index=True)
    month_start: datetime = Field(index=True)

    # Metadata
    metadata_: Optional[dict] = Field(default=None, sa_column=Column(JSON))
