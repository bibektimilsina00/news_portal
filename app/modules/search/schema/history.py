import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.modules.search.model.history import SearchHistory


# Base schemas
class SearchHistoryBase(SQLModel):
    query: str = Field(max_length=500, description="The search query")
    search_type: str = Field(max_length=50, description="Type of search performed")
    result_count: int = Field(default=0, description="Number of results returned")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Filters used in the search"
    )
    clicked_result_id: Optional[str] = Field(
        default=None, description="ID of the result that was clicked"
    )


# Public schemas
class SearchHistoryPublic(SearchHistoryBase):
    id: str
    user_id: str
    created_at: datetime


# Create schemas
class SearchHistoryCreate(SearchHistoryBase):
    pass


# Update schemas
class SearchHistoryUpdate(BaseModel):
    result_count: Optional[int] = None
    clicked_result_id: Optional[str] = None


# Response schemas
class SearchHistoryList(BaseModel):
    data: List[SearchHistoryPublic]
    total: int
    skip: int
    limit: int


class SearchHistoryStats(BaseModel):
    total_searches: int
    unique_queries: int
    most_searched_type: str
    average_results_per_search: float
