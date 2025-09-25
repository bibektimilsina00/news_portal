import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.search.crud.crud_search import (
    crud_search_history,
    crud_search_query,
    crud_search_result,
    crud_trending_topic,
)
from app.modules.search.model.search import SearchResultType, SearchType
from app.modules.search.schema.search import (
    SearchHistoryCreate,
    SearchQueryCreate,
    SearchRequest,
    SearchResponse,
    TrendingTopicCreate,
    TrendingTopicPublic,
    TrendingTopicsResponse,
)


class SearchService:
    def __init__(self):
        # In production, this would be Elasticsearch or similar
        self.search_backend = None

    def perform_search(
        self, session: Session, request: SearchRequest, user_id: Optional[UUID] = None
    ) -> SearchResponse:
        """Perform a search across the platform."""
        start_time = time.time()

        # Create search query record
        search_query_data = SearchQueryCreate(
            query=request.query,
            search_type=request.search_type,
            filters=request.filters,
        )
        search_query = crud_search_query.create(session, obj_in=search_query_data)
        if user_id:
            search_query.user_id = str(user_id)
            session.add(search_query)
            session.commit()
            session.refresh(search_query)

        # Perform the actual search (simplified implementation)
        results = self._execute_search(request)

        # Cache results
        self._cache_results(session, search_query.id, results, request.query)

        # Update trending topics
        self._update_trending_topics(session, request.query, request.search_type)

        # Add to search history if user is logged in
        if user_id:
            history_data = SearchHistoryCreate(
                query=request.query,
                search_type=request.search_type,
                filters=request.filters,
                result_count=len(results),
            )
            history = crud_search_history.create(session, obj_in=history_data)
            history.user_id = str(user_id)
            session.add(history)
            session.commit()

        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        return SearchResponse(
            query=request.query,
            search_type=request.search_type,
            total_results=len(results),
            results=results,
            search_time_ms=search_time,
        )

    def _execute_search(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Execute the actual search logic."""
        # This is a simplified implementation
        # In production, this would query Elasticsearch, database full-text search, etc.

        results = []

        if request.search_type == SearchType.POST:
            results = self._search_posts(request)
        elif request.search_type == SearchType.NEWS:
            results = self._search_news(request)
        elif request.search_type == SearchType.USER:
            results = self._search_users(request)
        elif request.search_type == SearchType.HASHTAG:
            results = self._search_hashtags(request)

        # Apply pagination
        start_idx = request.offset
        end_idx = start_idx + request.limit
        return results[start_idx:end_idx]

    def _search_posts(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Search posts (simplified)."""
        # In production, this would query the posts table with full-text search
        return [
            {
                "id": "post-1",
                "type": "post",
                "title": f"Post about {request.query}",
                "description": f"This is a post containing {request.query}",
                "thumbnail_url": None,
                "score": 0.95,
                "metadata": {"author": "user123", "likes": 42},
            }
        ]

    def _search_news(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Search news articles (simplified)."""
        # In production, this would query the news table
        return [
            {
                "id": "news-1",
                "type": "news",
                "title": f"News about {request.query}",
                "description": f"Breaking news: {request.query}",
                "thumbnail_url": None,
                "score": 0.88,
                "metadata": {"source": "NewsSource", "published_at": "2024-01-01"},
            }
        ]

    def _search_users(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Search users (simplified)."""
        # In production, this would query the users table
        return [
            {
                "id": "user-1",
                "type": "user",
                "title": f"User {request.query}",
                "description": f"Profile for {request.query}",
                "thumbnail_url": None,
                "score": 0.92,
                "metadata": {"followers": 1234, "verified": True},
            }
        ]

    def _search_hashtags(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Search hashtags (simplified)."""
        # In production, this would query trending topics or posts with hashtags
        return [
            {
                "id": f"hashtag-{request.query}",
                "type": "hashtag",
                "title": f"#{request.query}",
                "description": f"Posts tagged with #{request.query}",
                "thumbnail_url": None,
                "score": 0.85,
                "metadata": {"post_count": 567, "trending": True},
            }
        ]

    def _cache_results(
        self, session: Session, query_id: str, results: List[Dict[str, Any]], query: str
    ):
        """Cache search results for future use."""
        from app.modules.search.model.search import SearchResult

        query_hash = hashlib.md5(f"{query}".encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Cache for 1 hour

        for result in results:
            result_data = SearchResult(
                query_id=query_id,
                result_type=SearchResultType.CONTENT,  # Simplified
                entity_type=result["type"],
                entity_id=result["id"],
                title=result["title"],
                description=result.get("description"),
                thumbnail_url=result.get("thumbnail_url"),
                score=result["score"],
                metadata_={"query_hash": query_hash, **result.get("metadata", {})},
                expires_at=expires_at,
            )
            session.add(result_data)
        session.commit()

    def _update_trending_topics(
        self, session: Session, query: str, search_type: SearchType
    ):
        """Update trending topics based on search queries."""
        # Extract hashtags from query
        hashtags = [word[1:] for word in query.split() if word.startswith("#")]

        for hashtag in hashtags:
            topic = crud_trending_topic.get_by_topic(session, hashtag, "hashtag")
            if topic:
                crud_trending_topic.update_topic_metrics(
                    session, UUID(topic.id), search_count=1
                )
            else:
                # Create new trending topic
                from app.modules.search.schema.search import TrendingTopicCreate

                topic_data = TrendingTopicCreate(
                    topic=hashtag,
                    topic_type="hashtag",
                    search_count=1,
                )
                crud_trending_topic.create(session, obj_in=topic_data)

    def get_search_suggestions(
        self,
        session: Session,
        query: str,
        user_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> List[str]:
        """Get search suggestions based on partial query."""
        if user_id:
            # Get user's recent searches
            recent_queries = crud_search_query.get_recent_by_user(
                session, user_id, limit=limit
            )
            suggestions = [
                q.query for q in recent_queries if query.lower() in q.query.lower()
            ]
        else:
            # Get popular queries (simplified)
            popular = crud_search_history.get_popular_queries(session, limit=limit)
            suggestions = [
                item["query"]
                for item in popular
                if query.lower() in item["query"].lower()
            ]

        return suggestions[:limit]

    def get_trending_topics(
        self,
        session: Session,
        location: Optional[str] = None,
        language: str = "en",
        limit: int = 20,
    ) -> TrendingTopicsResponse:
        """Get trending topics."""
        topics = crud_trending_topic.get_trending(session, location, language, limit)

        return TrendingTopicsResponse(
            topics=[
                TrendingTopicPublic(
                    id=UUID(topic.id),
                    topic=topic.topic,
                    topic_type=topic.topic_type,
                    search_count=topic.search_count,
                    post_count=topic.post_count,
                    score=topic.engagement_score,  # Map engagement_score to score
                    location=topic.country_code
                    or topic.region,  # Use country_code or region for location
                    language="en",  # Default to English since model doesn't have language
                    created_at=topic.first_seen,
                    updated_at=topic.last_updated,
                    last_calculated=topic.last_updated,  # Use last_updated as last_calculated
                )
                for topic in topics
            ],
            total=len(topics),
            location=location,
            language=language,
        )

    def clear_user_search_history(self, session: Session, user_id: UUID) -> int:
        """Clear all search history for a user."""
        return crud_search_history.clear_user_history(session, user_id)

    def cleanup_expired_cache(self, session: Session) -> int:
        """Clean up expired search result cache."""
        return crud_search_result.cleanup_expired(session)


# Create service instance
search_service = SearchService()
