from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.modules.search.schema.search import (
    SearchRequest,
    SearchResponse,
    SearchSuggestionsResponse,
    TrendingTopicsResponse,
)
from app.modules.search.services.search_service import search_service
from app.shared.deps.deps import SessionDep, get_current_active_user

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(
    request: SearchRequest,
    session: SessionDep,
    current_user: Optional[dict] = Depends(get_current_active_user),
) -> SearchResponse:
    """
    Perform a search across the platform.
    """
    user_id = current_user.get("id") if current_user else None
    return search_service.perform_search(session, request, user_id)


@router.get("/search/suggestions", response_model=SearchSuggestionsResponse)
def get_search_suggestions(
    session: SessionDep,
    query: str = Query(
        ..., min_length=1, max_length=100, description="Partial search query"
    ),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    current_user: Optional[dict] = Depends(get_current_active_user),
) -> SearchSuggestionsResponse:
    """
    Get search suggestions based on partial query.
    """
    user_id = UUID(current_user["id"]) if current_user else None
    suggestions = search_service.get_search_suggestions(session, query, user_id, limit)

    return SearchSuggestionsResponse(
        suggestions=suggestions,
        query=query,
    )


@router.get("/trending", response_model=TrendingTopicsResponse)
def get_trending_topics(
    session: SessionDep,
    location: Optional[str] = Query(None, description="Filter by geographic location"),
    language: str = Query("en", description="Language for trending topics"),
    limit: int = Query(
        20, ge=1, le=50, description="Maximum number of trending topics"
    ),
) -> TrendingTopicsResponse:
    """
    Get trending topics across the platform.
    """
    return search_service.get_trending_topics(session, location, language, limit)


@router.delete("/search/history", response_model=Dict[str, Any])
def clear_search_history(
    session: SessionDep,
    current_user: dict = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Clear all search history for the current user.
    """
    user_id = UUID(current_user["id"])
    deleted_count = search_service.clear_user_search_history(session, user_id)

    return {
        "message": f"Deleted {deleted_count} search history items",
        "deleted_count": deleted_count,
    }


@router.post("/admin/search/cache/cleanup", response_model=Dict[str, Any])
def cleanup_expired_cache(
    session: SessionDep,
    current_user: dict = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Clean up expired search result cache (admin only).
    """
    # TODO: Add admin permission check
    cleaned_count = search_service.cleanup_expired_cache(session)

    return {
        "message": f"Cleaned up {cleaned_count} expired cache entries",
        "cleaned_count": cleaned_count,
    }
