import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class TrendingTopic(SQLModel, table=True):
    """Trending topics model"""

    __tablename__ = "trending_topics"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    # Topic details
    topic: str = Field(max_length=200, index=True, unique=True)
    topic_type: str = Field(
        max_length=50, default="hashtag"
    )  # "hashtag", "keyword", "location"
    category: Optional[str] = Field(
        default=None, max_length=100
    )  # "news", "sports", "entertainment", etc.

    # Metrics
    search_count: int = Field(default=0, ge=0)
    post_count: int = Field(default=0, ge=0)
    user_count: int = Field(default=0, ge=0)
    engagement_score: float = Field(default=0.0, ge=0)

    # Trending data
    rank: int = Field(default=0, ge=0)
    velocity: float = Field(default=0.0)  # Rate of growth
    peak_time: Optional[datetime] = None

    # Geographic data
    country_code: Optional[str] = Field(default=None, max_length=10)
    region: Optional[str] = Field(default=None, max_length=100)

    # Additional metadata
    metadata_: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Timestamps
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=24)
    )
