from typing import List, Optional

from sqlmodel import Session

from app.modules.search.crud.crud_trending import crud_trending_topic
from app.modules.search.model.trending import TrendingTopic
from app.modules.search.schema.trending import (
    TrendingTopicCreate,
    TrendingTopicPublic,
    TrendingTopicsList,
    TrendingTopicUpdate,
)


class TrendingTopicService:
    """Service layer for trending topics operations."""

    @staticmethod
    def create_trending_topic(
        session: Session, topic_in: TrendingTopicCreate
    ) -> TrendingTopic:
        """Create a new trending topic."""
        return crud_trending_topic.create(session, obj_in=topic_in)

    @staticmethod
    def get_trending_topics(
        session: Session, skip: int = 0, limit: int = 20
    ) -> List[TrendingTopic]:
        """Get active trending topics."""
        return crud_trending_topic.get_active_trending_topics(session, limit=limit)

    @staticmethod
    def get_trending_topic_by_id(
        session: Session, topic_id: str
    ) -> Optional[TrendingTopic]:
        """Get a trending topic by ID."""
        return crud_trending_topic.get_by_id(session, topic_id=topic_id)

    @staticmethod
    def get_trending_topic_by_name(
        session: Session, topic: str
    ) -> Optional[TrendingTopic]:
        """Get a trending topic by topic name."""
        return crud_trending_topic.get_by_topic(session, topic=topic)

    @staticmethod
    def get_trending_topics_by_category(
        session: Session, category: str, limit: int = 10
    ) -> List[TrendingTopic]:
        """Get trending topics for a specific category."""
        return crud_trending_topic.get_trending_topics_by_category(
            session, category=category, limit=limit
        )

    @staticmethod
    def update_trending_topic(
        session: Session, topic_id: str, topic_update: TrendingTopicUpdate
    ) -> Optional[TrendingTopic]:
        """Update a trending topic."""
        db_obj = crud_trending_topic.get_by_id(session, topic_id=topic_id)
        if db_obj:
            return crud_trending_topic.update(
                session, db_obj=db_obj, obj_in=topic_update.model_dump()
            )
        return None

    @staticmethod
    def delete_trending_topic(
        session: Session, topic_id: str
    ) -> Optional[TrendingTopic]:
        """Delete a trending topic."""
        return crud_trending_topic.remove_by_id(session, topic_id=topic_id)

    @staticmethod
    def increment_topic_engagement(
        session: Session, topic: str, increment: float = 1.0
    ) -> TrendingTopic:
        """Increment engagement score for a topic (creates if doesn't exist)."""
        return crud_trending_topic.increment_topic_engagement(
            session, topic=topic, increment=increment
        )

    @staticmethod
    def update_topic_score(
        session: Session, topic_id: str, new_score: float
    ) -> Optional[TrendingTopic]:
        """Update the engagement score of a trending topic."""
        return crud_trending_topic.update_topic_score(
            session, topic_id=topic_id, new_score=new_score
        )

    @staticmethod
    def cleanup_expired_topics(session: Session, hours_old: int = 24) -> int:
        """Clean up expired trending topics."""
        return crud_trending_topic.deactivate_old_topics(session, hours_old=hours_old)

    @staticmethod
    def get_trending_topics_response(
        session: Session, skip: int = 0, limit: int = 20
    ) -> TrendingTopicsList:
        """Get trending topics formatted for API response."""
        topics = crud_trending_topic.get_active_trending_topics(session, limit=limit)
        # Convert to public schema
        public_topics = [TrendingTopicPublic.model_validate(topic) for topic in topics]
        return TrendingTopicsList(data=public_topics, total=len(public_topics))


trending_topic_service = TrendingTopicService()
