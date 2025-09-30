from typing import Any, Dict, List, Optional

from sqlmodel import Session

from app.modules.search.crud.crud_history import crud_search_history
from app.modules.search.model.history import SearchHistory
from app.modules.search.schema.history import (
    SearchHistoryCreate,
    SearchHistoryStats,
    SearchHistoryUpdate,
)


class SearchHistoryService:
    """Service layer for search history operations."""

    @staticmethod
    def create_search_history(
        session: Session, history_in: SearchHistoryCreate
    ) -> SearchHistory:
        """Create a new search history entry."""
        return crud_search_history.create(session, obj_in=history_in)

    @staticmethod
    def get_user_search_history(
        session: Session, user_id: str, skip: int = 0, limit: int = 50
    ) -> List[SearchHistory]:
        """Get search history for a specific user."""
        return crud_search_history.get_user_history(
            session, user_id=user_id, skip=skip, limit=limit
        )

    @staticmethod
    def get_recent_searches(
        session: Session, user_id: str, limit: int = 10
    ) -> List[str]:
        """Get recent unique search queries for a user."""
        history_items = crud_search_history.get_user_history(
            session, user_id=user_id, skip=0, limit=100
        )

        # Extract unique queries, most recent first
        seen_queries = set()
        recent_queries = []

        for item in history_items:
            if item.query not in seen_queries:
                seen_queries.add(item.query)
                recent_queries.append(item.query)
                if len(recent_queries) >= limit:
                    break

        return recent_queries

    @staticmethod
    def delete_search_history(
        session: Session, history_id: str, user_id: str
    ) -> Optional[SearchHistory]:
        """Delete a specific search history entry (user can only delete their own)."""
        history_item = crud_search_history.get(session, id=history_id)
        if history_item and str(history_item.user_id) == user_id:
            return crud_search_history.remove(session, id=history_id)
        return None

    @staticmethod
    def clear_user_history(session: Session, user_id: str) -> int:
        """Clear all search history for a user."""
        return crud_search_history.clear_user_history(session, user_id=user_id)

    @staticmethod
    def get_popular_queries(session: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get globally popular search queries."""
        return crud_search_history.get_popular_queries(session, limit=limit)

    @staticmethod
    def get_search_stats(session: Session, user_id: str) -> SearchHistoryStats:
        """Get search statistics for a user."""
        stats = crud_search_history.get_search_stats(session, user_id=user_id)
        return SearchHistoryStats(**stats)

    @staticmethod
    def update_search_history(
        session: Session, history_id: str, history_update: SearchHistoryUpdate
    ) -> Optional[SearchHistory]:
        """Update a search history entry."""
        return crud_search_history.update(
            session,
            db_obj=crud_search_history.get(session, id=history_id),
            obj_in=history_update,
        )


search_history_service = SearchHistoryService()
