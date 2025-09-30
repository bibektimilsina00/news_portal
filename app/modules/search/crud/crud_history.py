from datetime import datetime
from typing import Any, Dict, List

from sqlmodel import Session, desc, select

from app.modules.search.model.history import SearchHistory
from app.modules.search.schema.history import SearchHistoryCreate, SearchHistoryUpdate
from app.shared.crud.base import CRUDBase


class CRUDSearchHistory(
    CRUDBase[SearchHistory, SearchHistoryCreate, SearchHistoryUpdate]
):
    def get_by_user(
        self, session: Session, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[SearchHistory]:
        """Get search history by user ID."""
        return list(
            session.exec(
                select(SearchHistory)
                .where(SearchHistory.user_id == user_id)
                .order_by(desc(SearchHistory.created_at))
                .offset(skip)
                .limit(limit)
            )
        )

    def get_recent_by_user(
        self, session: Session, user_id: str, limit: int = 10
    ) -> List[SearchHistory]:
        """Get recent search history for a user."""
        return list(
            session.exec(
                select(SearchHistory)
                .where(SearchHistory.user_id == user_id)
                .order_by(desc(SearchHistory.created_at))
                .limit(limit)
            )
        )

    def get_popular_queries(
        self, session: Session, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most popular search queries across all users."""
        # Get all search history items
        history_items = list(session.exec(select(SearchHistory)))

        # Count query frequencies
        query_counts: dict[str, int] = {}
        for item in history_items:
            query = item.query.lower().strip()
            if query:
                query_counts[query] = query_counts.get(query, 0) + 1

        # Sort by frequency and get top queries
        popular_queries = sorted(
            query_counts.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        return [{"query": query, "count": count} for query, count in popular_queries]

    def get_search_stats(self, session: Session, user_id: str) -> Dict[str, Any]:
        """Get search statistics for a user."""
        # Get total searches (simplified)
        history_items = list(
            session.exec(select(SearchHistory).where(SearchHistory.user_id == user_id))
        )
        total_searches = len(history_items)

        # Get unique queries
        unique_queries = len(set(item.query for item in history_items))

        # Get most used search type (simplified)
        type_counts: dict[str, int] = {}
        for item in history_items:
            type_counts[item.search_type] = type_counts.get(item.search_type, 0) + 1

        most_searched_type = (
            max(type_counts.keys(), key=lambda k: type_counts[k])
            if type_counts
            else "general"
        )

        # Get average results per search
        if history_items:
            avg_results = sum(item.result_count for item in history_items) / len(
                history_items
            )
        else:
            avg_results = 0.0

        return {
            "total_searches": total_searches,
            "unique_queries": unique_queries,
            "most_searched_type": most_searched_type,
            "average_results_per_search": round(avg_results, 2),
        }

    def clear_user_history(self, session: Session, user_id: str) -> int:
        """Clear all search history for a user."""
        history_items = list(
            session.exec(select(SearchHistory).where(SearchHistory.user_id == user_id))
        )
        count = 0
        for item in history_items:
            session.delete(item)
            count += 1
        session.commit()
        return count

    def delete_old_history(self, session: Session, days_old: int = 30) -> int:
        """Delete search history older than specified days."""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        old_items = list(
            session.exec(
                select(SearchHistory).where(SearchHistory.created_at < cutoff_date)
            )
        )
        count = 0
        for item in old_items:
            session.delete(item)
            count += 1
        session.commit()
        return count


crud_search_history = CRUDSearchHistory(SearchHistory)
