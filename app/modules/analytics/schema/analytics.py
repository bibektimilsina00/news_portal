import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel


# Base schemas
class UserAnalyticsBase(SQLModel):
    user_id: str = Field(description="User ID for analytics")
    profile_views: int = Field(default=0, description="Number of profile views")
    follower_count: int = Field(default=0, description="Current follower count")
    following_count: int = Field(default=0, description="Current following count")
    total_posts: int = Field(default=0, description="Total posts created")
    total_likes_received: int = Field(
        default=0, description="Total likes received on posts"
    )
    total_comments_received: int = Field(
        default=0, description="Total comments received on posts"
    )
    total_shares_received: int = Field(
        default=0, description="Total shares received on posts"
    )
    total_bookmarks_received: int = Field(
        default=0, description="Total bookmarks received on posts"
    )
    avg_engagement_rate: float = Field(
        default=0.0, description="Average engagement rate"
    )
    login_count: int = Field(default=0, description="Number of logins")
    session_duration_avg: int = Field(
        default=0, description="Average session duration in seconds"
    )
    total_earnings: float = Field(
        default=0.0, description="Total earnings from monetization"
    )
    subscription_count: int = Field(default=0, description="Number of subscribers")


class ContentAnalyticsBase(SQLModel):
    content_id: str = Field(description="Content ID (post, story, reel, etc.)")
    content_type: str = Field(
        description="Type of content: post, story, reel, news, live_stream"
    )
    author_id: str = Field(description="Author/creator of the content")
    views: int = Field(default=0, description="Number of views")
    likes: int = Field(default=0, description="Number of likes")
    comments: int = Field(default=0, description="Number of comments")
    shares: int = Field(default=0, description="Number of shares")
    bookmarks: int = Field(default=0, description="Number of bookmarks")
    engagement_rate: float = Field(
        default=0.0, description="Engagement rate percentage"
    )
    click_through_rate: float = Field(default=0.0, description="Click-through rate")
    average_view_duration: int = Field(
        default=0, description="Average view duration in seconds"
    )
    performance_score: float = Field(
        default=0.0, description="Performance score for ranking"
    )


class PlatformAnalyticsBase(SQLModel):
    total_users: int = Field(default=0, description="Total registered users")
    active_users_daily: int = Field(default=0, description="Daily active users")
    active_users_weekly: int = Field(default=0, description="Weekly active users")
    active_users_monthly: int = Field(default=0, description="Monthly active users")
    total_posts: int = Field(default=0, description="Total posts created")
    total_stories: int = Field(default=0, description="Total stories created")
    total_reels: int = Field(default=0, description="Total reels created")
    total_news_articles: int = Field(default=0, description="Total news articles")
    total_live_streams: int = Field(default=0, description="Total live streams")
    total_likes: int = Field(default=0, description="Total likes across platform")
    total_comments: int = Field(default=0, description="Total comments across platform")
    total_shares: int = Field(default=0, description="Total shares across platform")
    total_bookmarks: int = Field(
        default=0, description="Total bookmarks across platform"
    )
    total_revenue: float = Field(default=0.0, description="Total platform revenue")


# Public schemas
class UserAnalyticsPublic(UserAnalyticsBase):
    id: str
    date_recorded: datetime
    week_start: datetime
    month_start: datetime
    audience_locations: Optional[Dict[str, Any]] = None
    audience_age_groups: Optional[Dict[str, Any]] = None
    audience_genders: Optional[Dict[str, Any]] = None
    top_performing_post_id: Optional[str] = None
    top_performing_score: float = 0.0
    last_login_at: Optional[datetime] = None


class ContentAnalyticsPublic(ContentAnalyticsBase):
    id: str
    date_recorded: datetime
    content_created_at: datetime
    viewer_locations: Optional[Dict[str, Any]] = None
    device_types: Optional[Dict[str, Any]] = None
    platforms: Optional[Dict[str, Any]] = None
    video_completion_rate: Optional[float] = None
    story_completion_rate: Optional[float] = None
    live_viewer_peak: Optional[int] = None
    live_duration: Optional[int] = None


class PlatformAnalyticsPublic(PlatformAnalyticsBase):
    id: str
    date_recorded: datetime
    week_start: datetime
    month_start: datetime
    top_countries: Optional[Dict[str, Any]] = None
    top_cities: Optional[Dict[str, Any]] = None
    device_breakdown: Optional[Dict[str, Any]] = None
    platform_breakdown: Optional[Dict[str, Any]] = None
    subscription_revenue: float = 0.0
    ad_revenue: float = 0.0


# Create schemas
class UserAnalyticsCreate(UserAnalyticsBase):
    pass


class ContentAnalyticsCreate(ContentAnalyticsBase):
    pass


class PlatformAnalyticsCreate(PlatformAnalyticsBase):
    pass


# Update schemas
class UserAnalyticsUpdate(BaseModel):
    profile_views: Optional[int] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    total_posts: Optional[int] = None
    total_likes_received: Optional[int] = None
    total_comments_received: Optional[int] = None
    total_shares_received: Optional[int] = None
    total_bookmarks_received: Optional[int] = None
    avg_engagement_rate: Optional[float] = None
    login_count: Optional[int] = None
    session_duration_avg: Optional[int] = None
    total_earnings: Optional[float] = None
    subscription_count: Optional[int] = None


class ContentAnalyticsUpdate(BaseModel):
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    bookmarks: Optional[int] = None
    engagement_rate: Optional[float] = None
    click_through_rate: Optional[float] = None
    average_view_duration: Optional[int] = None
    performance_score: Optional[float] = None


class PlatformAnalyticsUpdate(BaseModel):
    total_users: Optional[int] = None
    active_users_daily: Optional[int] = None
    active_users_weekly: Optional[int] = None
    active_users_monthly: Optional[int] = None
    total_posts: Optional[int] = None
    total_stories: Optional[int] = None
    total_reels: Optional[int] = None
    total_news_articles: Optional[int] = None
    total_live_streams: Optional[int] = None
    total_likes: Optional[int] = None
    total_comments: Optional[int] = None
    total_shares: Optional[int] = None
    total_bookmarks: Optional[int] = None
    total_revenue: Optional[float] = None


# Response schemas
class UserAnalyticsList(BaseModel):
    data: List[UserAnalyticsPublic]
    total: int
    user_id: str


class ContentAnalyticsList(BaseModel):
    data: List[ContentAnalyticsPublic]
    total: int
    content_type: Optional[str] = None
    author_id: Optional[str] = None


class PlatformAnalyticsList(BaseModel):
    data: List[PlatformAnalyticsPublic]
    total: int


class AnalyticsSummary(BaseModel):
    """Summary of key analytics metrics"""

    total_users: int
    active_users_today: int
    total_content: int
    total_engagement: int
    top_performing_content: List[Dict[str, Any]]
    user_growth_trend: List[Dict[str, Any]]
    revenue_trend: Optional[List[Dict[str, Any]]] = None


class DateRangeFilter(BaseModel):
    """Date range filter for analytics queries"""

    start_date: datetime
    end_date: datetime
    granularity: str = Field(default="daily", description="daily, weekly, or monthly")
