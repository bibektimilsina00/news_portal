import enum
import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class SearchType(str, enum.Enum):
    """Types of searchable content"""

    POST = "post"
    NEWS = "news"
    USER = "user"
    HASHTAG = "hashtag"
    LOCATION = "location"
    STORY = "story"
    REEL = "reel"
    LIVE_STREAM = "live_stream"


class SearchResultType(str, enum.Enum):
    """Types of search results"""

    CONTENT = "content"
    USER = "user"
    HASHTAG = "hashtag"
    LOCATION = "location"
    TRENDING = "trending"


class SearchQuery(SQLModel, table=True):
    """Search query model for tracking searches"""


    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    # Search details
    query: str = Field(max_length=500, index=True)
    search_type: SearchType = Field(sa_column=Column(Enum(SearchType)))
    filters: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # User who performed the search
    user_id: Optional[str] = Field(default=None, foreign_key="user.id", index=True)

    # Search metadata
    result_count: int = Field(default=0, ge=0)
    search_duration: float = Field(default=0.0, ge=0)  # in seconds

    # Location data (if location-based search)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = None  # search radius in km

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="search_queries")


class SearchResult(SQLModel, table=True):
    """Search result model for caching results"""


    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    # Link to search query
    query_id: str = Field(foreign_key="searchquery.id", index=True)

    # Result details
    result_type: SearchResultType = Field(sa_column=Column(Enum(SearchResultType)))
    entity_type: str = Field(max_length=50)  # "post", "user", "news", etc.
    entity_id: str = Field(max_length=100)  # UUID or ID of the entity
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=1000)
    thumbnail_url: Optional[str] = Field(default=None, max_length=1000)

    # Search relevance
    score: float = Field(default=0.0, ge=0)
    rank: int = Field(default=0, ge=0)

    # Additional metadata
    metadata_: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=1)
    )

    # Relationships
    query: "SearchQuery" = Relationship(back_populates="results")


# Add relationships to SearchQuery
SearchQuery.results = Relationship(back_populates="query", cascade_delete=True)
