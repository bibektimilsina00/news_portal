from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel


# Base schemas
class TrendingTopicBase(SQLModel):
    topic: str = Field(max_length=200, description="The trending topic or hashtag")
    topic_type: str = Field(
        max_length=50, description="Type of topic (hashtag, keyword, etc.)"
    )
    category: Optional[str] = Field(
        default=None, max_length=100, description="Category (news, sports, etc.)"
    )
    search_count: int = Field(
        default=0, description="Number of searches for this topic"
    )
    post_count: int = Field(
        default=0, description="Number of posts containing this topic"
    )
    user_count: int = Field(
        default=0, description="Number of users mentioning this topic"
    )
    engagement_score: float = Field(default=0.0, description="Overall engagement score")
    rank: int = Field(default=0, description="Current ranking position")
    velocity: float = Field(default=0.0, description="Rate of growth")
    country_code: Optional[str] = Field(
        default=None, max_length=10, description="Country code"
    )
    region: Optional[str] = Field(
        default=None, max_length=100, description="Geographic region"
    )


# Public schemas
class TrendingTopicPublic(TrendingTopicBase):
    id: str
    first_seen: datetime
    last_updated: datetime
    expires_at: datetime


# Create schemas
class TrendingTopicCreate(TrendingTopicBase):
    pass


# Update schemas
class TrendingTopicUpdate(BaseModel):
    search_count: Optional[int] = None
    post_count: Optional[int] = None
    user_count: Optional[int] = None
    engagement_score: Optional[float] = None
    rank: Optional[int] = None
    velocity: Optional[float] = None


# Response schemas
class TrendingTopicsList(BaseModel):
    data: List[TrendingTopicPublic]
    total: int
    location: Optional[str] = None
    language: str = "en"


class TrendingTopicStats(BaseModel):
    total_topics: int
    active_topics: int
    top_category: str
    average_engagement: float
    trending_velocity: float
