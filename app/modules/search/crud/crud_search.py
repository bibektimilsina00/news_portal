from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, desc, func, select

from app.modules.search.model.history import SearchHistory
from app.modules.search.model.search import SearchQuery, SearchResult
from app.modules.search.model.trending import TrendingTopic
from app.modules.search.schema.search import (
    SearchHistoryCreate,
    SearchHistoryUpdate,
    SearchQueryCreate,
    SearchQueryUpdate,
    TrendingTopicCreate,
    TrendingTopicUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDSearchQuery(CRUDBase[SearchQuery, SearchQueryCreate, SearchQueryUpdate]):
    def get_by_user(
        self, session: Session, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[SearchQuery]:
        """Get search queries by user ID."""
        return list(
            session.exec(
                select(SearchQuery)
                .where(SearchQuery.user_id == user_id)
                .order_by(desc(SearchQuery.created_at))
                .offset(skip)
                .limit(limit)
            )
        )

    def get_recent_by_user(
        self, session: Session, user_id: UUID, limit: int = 10
    ) -> List[SearchQuery]:
        """Get recent search queries by user."""
        return list(
            session.exec(
                select(SearchQuery)
                .where(SearchQuery.user_id == user_id)
                .order_by(desc(SearchQuery.created_at))
                .limit(limit)
            )
        )

    def search_similar(
        self,
        session: Session,
        query: str,
        search_type: str,
        user_id: Optional[UUID] = None,
    ) -> List[SearchQuery]:
        """Find similar search queries."""
        stmt = select(SearchQuery).where(
            func.lower(SearchQuery.query).contains(func.lower(query)),
            SearchQuery.search_type == search_type,
        )
        if user_id:
            stmt = stmt.where(SearchQuery.user_id == user_id)
        return list(session.exec(stmt.order_by(desc(SearchQuery.created_at))))


class CRUDSearchResult(CRUDBase[SearchResult, Any, Any]):
    def get_by_query(self, session: Session, query_id: UUID) -> List[SearchResult]:
        """Get search results for a specific query."""
        return list(
            session.exec(
                select(SearchResult)
                .where(SearchResult.query_id == query_id)
                .order_by(desc(SearchResult.score))
            )
        )

    def get_cached_results(
        self, session: Session, query_hash: str
    ) -> Optional[List[SearchResult]]:
        """Get cached search results if not expired."""
        results = list(
            session.exec(
                select(SearchResult)
                .where(SearchResult.expires_at > datetime.utcnow())
                .order_by(desc(SearchResult.score))
            )
        )
        # Filter by query_hash in metadata (simplified - in real implementation use proper JSON querying)
        return [
            r
            for r in results
            if r.metadata and r.metadata.get("query_hash") == query_hash
        ] or None

    def cleanup_expired(self, session: Session) -> int:
        """Remove expired cached results."""
        expired_results = session.exec(
            select(SearchResult).where(SearchResult.expires_at <= datetime.utcnow())
        )
        count = 0
        for result in expired_results:
            session.delete(result)
            count += 1
        session.commit()
        return count


class CRUDSearchHistory(
    CRUDBase[SearchHistory, SearchHistoryCreate, SearchHistoryUpdate]
):
    def get_by_user(
        self, session: Session, user_id: UUID, skip: int = 0, limit: int = 100
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

    def get_popular_queries(
        self, session: Session, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get most popular search queries."""
        # Simplified implementation - in production use proper aggregation
        results = list(
            session.exec(
                select(SearchHistory.query, SearchHistory.search_type)
                .group_by(SearchHistory.query, SearchHistory.search_type)
                .order_by(desc(SearchHistory.created_at))
                .limit(limit)
            )
        )
        return [{"query": r[0], "search_type": r[1]} for r in results]

    def clear_user_history(self, session: Session, user_id: UUID) -> int:
        """Clear all search history for a user."""
        history_items = session.exec(
            select(SearchHistory).where(SearchHistory.user_id == user_id)
        )
        count = 0
        for item in history_items:
            session.delete(item)
            count += 1
        session.commit()
        return count


class CRUDTrendingTopic(
    CRUDBase[TrendingTopic, TrendingTopicCreate, TrendingTopicUpdate]
):
    def get_trending(
        self,
        session: Session,
        location: Optional[str] = None,
        language: str = "en",
        limit: int = 20,
    ) -> List[TrendingTopic]:
        """Get trending topics."""
        stmt = select(TrendingTopic).where(TrendingTopic.language == language)
        if location:
            stmt = stmt.where(TrendingTopic.location == location)
        return list(session.exec(stmt.order_by(desc(TrendingTopic.score)).limit(limit)))

    def get_by_topic(
        self, session: Session, topic: str, topic_type: str
    ) -> Optional[TrendingTopic]:
        """Get trending topic by topic name and type."""
        return session.exec(
            select(TrendingTopic).where(
                TrendingTopic.topic == topic, TrendingTopic.topic_type == topic_type
            )
        ).first()

    def update_topic_metrics(
        self,
        session: Session,
        topic_id: UUID,
        search_count: int = 0,
        post_count: int = 0,
    ) -> Optional[TrendingTopic]:
        """Update search and post counts for a trending topic."""
        topic = session.get(TrendingTopic, topic_id)
        if topic:
            topic.search_count += search_count
            topic.post_count += post_count
            # Simple trending score calculation
            topic.score = (topic.search_count * 0.7) + (topic.post_count * 0.3)
            session.add(topic)
            session.commit()
            session.refresh(topic)
        return topic

    def recalculate_scores(self, session: Session) -> int:
        """Recalculate trending scores for all topics."""
        # This is a simplified implementation
        # In production, you'd use more sophisticated algorithms
        topics = list(session.exec(select(TrendingTopic)))
        for topic in topics:
            # Decay old scores and recalculate
            topic.score = (topic.search_count * 0.7) + (topic.post_count * 0.3)
            topic.last_calculated = datetime.utcnow()
            session.add(topic)
        session.commit()
        return len(topics)


# Create CRUD instances
crud_search_query = CRUDSearchQuery(SearchQuery)
crud_search_result = CRUDSearchResult(SearchResult)
crud_search_history = CRUDSearchHistory(SearchHistory)
crud_trending_topic = CRUDTrendingTopic(TrendingTopic)


class CRUDSearchResult(CRUDBase[SearchResult, Any, Any]):
    def get_by_query(self, session: Session, query_id: UUID) -> List[SearchResult]:
        """Get search results for a specific query."""
        return session.exec(
            select(SearchResult)
            .where(SearchResult.query_id == query_id)
            .order_by(SearchResult.score.desc())
        ).all()

    def get_cached_results(
        self, session: Session, query_hash: str
    ) -> Optional[List[SearchResult]]:
        """Get cached search results if not expired."""
        from datetime import datetime

        return session.exec(
            select(SearchResult)
            .where(
                SearchResult.query.query_hash == query_hash,
                SearchResult.expires_at > datetime.utcnow(),
            )
            .order_by(SearchResult.score.desc())
        ).all()

    def cleanup_expired(self, session: Session) -> int:
        """Remove expired cached results."""
        from datetime import datetime

        from sqlmodel import delete

        result = session.exec(
            delete(SearchResult).where(SearchResult.expires_at <= datetime.utcnow())
        )
        session.commit()
        return result.rowcount


class CRUDSearchHistory(
    CRUDBase[SearchHistory, SearchHistoryCreate, SearchHistoryUpdate]
):
    def get_by_user(
        self, session: Session, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[SearchHistory]:
        """Get search history by user ID."""
        return session.exec(
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_popular_queries(
        self, session: Session, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get most popular search queries."""
        # This would typically use aggregation, but for simplicity we'll return recent queries
        # In a real implementation, you'd use SQL aggregation functions
        return session.exec(
            select(SearchHistory.query, SearchHistory.search_type)
            .group_by(SearchHistory.query, SearchHistory.search_type)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        ).all()

    def clear_user_history(self, session: Session, user_id: UUID) -> int:
        """Clear all search history for a user."""
        from sqlmodel import delete

        result = session.exec(
            delete(SearchHistory).where(SearchHistory.user_id == user_id)
        )
        session.commit()
        return result.rowcount


class CRUDTrendingTopic(
    CRUDBase[TrendingTopic, TrendingTopicCreate, TrendingTopicUpdate]
):
    def get_trending(
        self,
        session: Session,
        location: Optional[str] = None,
        language: str = "en",
        limit: int = 20,
    ) -> List[TrendingTopic]:
        """Get trending topics."""
        stmt = select(TrendingTopic).where(TrendingTopic.language == language)
        if location:
            stmt = stmt.where(TrendingTopic.location == location)
        return session.exec(
            stmt.order_by(TrendingTopic.score.desc()).limit(limit)
        ).all()

    def get_by_topic(
        self, session: Session, topic: str, topic_type: str
    ) -> Optional[TrendingTopic]:
        """Get trending topic by topic name and type."""
        return session.exec(
            select(TrendingTopic).where(
                TrendingTopic.topic == topic, TrendingTopic.topic_type == topic_type
            )
        ).first()

    def update_topic_metrics(
        self,
        session: Session,
        topic_id: UUID,
        search_count: int = 0,
        post_count: int = 0,
    ) -> Optional[TrendingTopic]:
        """Update search and post counts for a trending topic."""
        topic = session.get(TrendingTopic, topic_id)
        if topic:
            topic.search_count += search_count
            topic.post_count += post_count
            # Simple trending score calculation
            topic.score = (topic.search_count * 0.7) + (topic.post_count * 0.3)
            session.add(topic)
            session.commit()
            session.refresh(topic)
        return topic

    def recalculate_scores(self, session: Session) -> int:
        """Recalculate trending scores for all topics."""
        # This is a simplified implementation
        # In production, you'd use more sophisticated algorithms
        topics = session.exec(select(TrendingTopic)).all()
        for topic in topics:
            # Decay old scores and recalculate
            topic.score = (topic.search_count * 0.7) + (topic.post_count * 0.3)
            topic.last_calculated = datetime.utcnow()
            session.add(topic)
        session.commit()
        return len(topics)


# Create CRUD instances
crud_search_query = CRUDSearchQuery(SearchQuery)
crud_search_result = CRUDSearchResult(SearchResult)
crud_search_history = CRUDSearchHistory(SearchHistory)
crud_trending_topic = CRUDTrendingTopic(TrendingTopic)
