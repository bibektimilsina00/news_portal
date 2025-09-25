import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.modules.search.model.search import SearchResultType, SearchType


# Base schemas
class SearchQueryBase(SQLModel):
    query: str = Field(max_length=500, description="The search query text")
    search_type: SearchType = Field(description="Type of search being performed")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional search filters"
    )
    location: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Geographic location for location-based search",
    )


class SearchResultBase(SQLModel):
    result_type: SearchResultType = Field(description="Type of search result")
    result_id: uuid.UUID = Field(description="ID of the result entity")
    title: str = Field(max_length=200, description="Display title of the result")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Brief description of the result"
    )
    thumbnail_url: Optional[str] = Field(
        default=None, max_length=500, description="URL to thumbnail image"
    )
    metadata_: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata for the result"
    )
    score: float = Field(default=0.0, description="Search relevance score")


class SearchHistoryBase(SQLModel):
    query: str = Field(max_length=500, description="The search query")
    search_type: SearchType = Field(description="Type of search performed")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Filters used in the search"
    )
    result_count: int = Field(default=0, description="Number of results returned")
    clicked_result_id: Optional[uuid.UUID] = Field(
        default=None, description="ID of the result that was clicked"
    )


class TrendingTopicBase(SQLModel):
    topic: str = Field(max_length=100, description="The trending topic or hashtag")
    topic_type: str = Field(
        max_length=50, description="Type of topic (hashtag, keyword, etc.)"
    )
    search_count: int = Field(
        default=0, description="Number of searches for this topic"
    )
    post_count: int = Field(
        default=0, description="Number of posts containing this topic"
    )
    score: float = Field(
        default=0.0, description="Trending score based on recency and volume"
    )
    location: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Geographic location if location-specific",
    )
    language: str = Field(
        default="en", max_length=10, description="Language of the topic"
    )


# Public schemas
class SearchQueryPublic(SearchQueryBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SearchResultPublic(SearchResultBase):
    id: uuid.UUID
    query_id: uuid.UUID
    created_at: datetime
    expires_at: datetime


class SearchHistoryPublic(SearchHistoryBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


class TrendingTopicPublic(TrendingTopicBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_calculated: datetime


# Create schemas
class SearchQueryCreate(SearchQueryBase):
    pass


class SearchHistoryCreate(SearchHistoryBase):
    pass


class TrendingTopicCreate(TrendingTopicBase):
    pass


# Update schemas
class SearchQueryUpdate(BaseModel):
    query: Optional[str] = Field(default=None, max_length=500)
    search_type: Optional[SearchType] = None
    filters: Optional[Dict[str, Any]] = None
    location: Optional[str] = None


class SearchHistoryUpdate(BaseModel):
    result_count: Optional[int] = None
    clicked_result_id: Optional[uuid.UUID] = None


class TrendingTopicUpdate(BaseModel):
    search_count: Optional[int] = None
    post_count: Optional[int] = None
    score: Optional[float] = None


# Search request/response schemas
class SearchRequest(BaseModel):
    query: str = Field(..., max_length=500, description="Search query text")
    search_type: SearchType = Field(..., description="Type of search to perform")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional filters"
    )
    location: Optional[str] = Field(
        default=None, max_length=100, description="Location filter"
    )
    limit: int = Field(
        default=20, ge=1, le=100, description="Maximum number of results"
    )
    offset: int = Field(default=0, ge=0, description="Pagination offset")


class SearchResponse(BaseModel):
    query: str
    search_type: SearchType
    total_results: int
    results: List[Dict[str, Any]]
    trending_topics: Optional[List[TrendingTopicPublic]] = None
    search_time_ms: float


class TrendingTopicsResponse(BaseModel):
    topics: List[TrendingTopicPublic]
    total: int
    location: Optional[str] = None
    language: str = "en"


class SearchSuggestionsResponse(BaseModel):
    suggestions: List[str]
    query: str
