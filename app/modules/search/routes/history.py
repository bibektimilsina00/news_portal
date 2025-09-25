from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.modules.search.model.history import SearchHistory
from app.modules.search.schema.history import (
    SearchHistoryCreate,
    SearchHistoryPublic,
    SearchHistoryStats,
)
from app.modules.search.services.history_service import search_history_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=SearchHistoryPublic)
def create_search_history(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    history_in: SearchHistoryCreate,
) -> SearchHistory:
    """
    Create a new search history entry.
    """
    # Ensure the history belongs to the current user
    history_in.user_id = current_user.id
    return search_history_service.create_search_history(session, history_in)


@router.get("/my-history", response_model=List[SearchHistoryPublic])
def get_my_search_history(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> List[SearchHistory]:
    """
    Get current user's search history.
    """
    return search_history_service.get_user_search_history(
        session, user_id=str(current_user.id), skip=skip, limit=limit
    )


@router.get("/recent-queries", response_model=List[str])
def get_recent_search_queries(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
) -> List[str]:
    """
    Get recent unique search queries for current user.
    """
    return search_history_service.get_recent_searches(
        session, user_id=str(current_user.id), limit=limit
    )


@router.delete("/{history_id}", response_model=SearchHistoryPublic)
def delete_search_history(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    history_id: str,
) -> SearchHistory:
    """
    Delete a specific search history entry (users can only delete their own).
    """
    history = search_history_service.delete_search_history(
        session, history_id=history_id, user_id=str(current_user.id)
    )
    if not history:
        raise HTTPException(
            status_code=404, detail="Search history not found or access denied"
        )
    return history


@router.delete("/clear-all", response_model=dict)
def clear_search_history(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """
    Clear all search history for current user.
    """
    deleted_count = search_history_service.clear_user_history(
        session, user_id=str(current_user.id)
    )
    return {"message": f"Deleted {deleted_count} search history entries"}


@router.get("/stats", response_model=SearchHistoryStats)
def get_search_stats(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> SearchHistoryStats:
    """
    Get search statistics for current user.
    """
    return search_history_service.get_search_stats(
        session, user_id=str(current_user.id)
    )


@router.get("/popular", response_model=List[dict])
def get_popular_queries(
    *,
    session: SessionDep,
    limit: int = Query(10, ge=1, le=50),
) -> List[dict]:
    """
    Get globally popular search queries.
    """
    return search_history_service.get_popular_queries(session, limit=limit)
