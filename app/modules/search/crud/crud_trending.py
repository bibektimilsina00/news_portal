from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, desc, select

from app.modules.search.model.trending import TrendingTopic
from app.shared.crud.base import CRUDBase


class CRUDTrendingTopic(CRUDBase[TrendingTopic, TrendingTopic, TrendingTopic]):
    def get_by_id(self, session: Session, topic_id: str) -> Optional[TrendingTopic]:
        """Get trending topic by string ID."""
        return session.get(TrendingTopic, topic_id)

    def remove_by_id(self, session: Session, topic_id: str) -> Optional[TrendingTopic]:
        """Remove trending topic by string ID."""
        obj = session.get(TrendingTopic, topic_id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj

    def get_by_topic(self, session: Session, topic: str) -> Optional[TrendingTopic]:
        """Get trending topic by topic name."""
        return session.exec(
            select(TrendingTopic).where(TrendingTopic.topic == topic)
        ).first()

    def get_active_trending_topics(
        self, session: Session, limit: int = 20
    ) -> List[TrendingTopic]:
        """Get currently active trending topics ordered by engagement score."""
        return list(
            session.exec(
                select(TrendingTopic)
                .where(TrendingTopic.expires_at > datetime.utcnow())
                .order_by(TrendingTopic.engagement_score.desc())
                .limit(limit)
            )
        )

    def get_trending_topics_by_category(
        self, session: Session, category: str, limit: int = 10
    ) -> List[TrendingTopic]:
        """Get trending topics for a specific category."""
        return list(
            session.exec(
                select(TrendingTopic)
                .where(
                    TrendingTopic.category == category,
                    TrendingTopic.expires_at > datetime.utcnow(),
                )
                .order_by(TrendingTopic.engagement_score.desc())
                .limit(limit)
            )
        )

    def update_topic_score(
        self, session: Session, topic_id: str, new_score: float
    ) -> Optional[TrendingTopic]:
        """Update the engagement score of a trending topic."""
        topic = session.get(TrendingTopic, topic_id)
        if topic:
            topic.engagement_score = new_score
            topic.last_updated = datetime.utcnow()
            session.add(topic)
            session.commit()
            session.refresh(topic)
        return topic

    def deactivate_old_topics(self, session: Session, hours_old: int = 24) -> int:
        """Deactivate trending topics older than specified hours."""
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
        result = session.exec(
            select(TrendingTopic).where(TrendingTopic.expires_at < cutoff_time)
        )
        old_topics = list(result)

        # Mark as expired by setting expires_at to now
        for topic in old_topics:
            topic.expires_at = datetime.utcnow()
            session.add(topic)

        session.commit()
        return len(old_topics)

    def increment_topic_engagement(
        self, session: Session, topic: str, increment: float = 1.0
    ) -> TrendingTopic:
        """Increment engagement score for a topic, creating it if it doesn't exist."""
        existing_topic = self.get_by_topic(session, topic)
        if existing_topic:
            existing_topic.engagement_score += increment
            existing_topic.search_count += 1
            existing_topic.last_updated = datetime.utcnow()
            session.add(existing_topic)
            session.commit()
            session.refresh(existing_topic)
            return existing_topic
        else:
            # Create new trending topic
            new_topic = TrendingTopic(
                topic=topic,
                search_count=1,
                engagement_score=increment,
                category="general",  # Default category
            )
            session.add(new_topic)
            session.commit()
            session.refresh(new_topic)
            return new_topic


crud_trending_topic = CRUDTrendingTopic(TrendingTopic)


crud_trending_topic = CRUDTrendingTopic(TrendingTopic)
