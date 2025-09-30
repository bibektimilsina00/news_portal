import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_
from sqlmodel import Session, case, select

from app.modules.news.model.news import News, NewsPriority, NewsStatus
from app.modules.news.schema.news import NewsCreate, NewsUpdate
from app.shared.crud.base import CRUDBase


class CRUDNews(CRUDBase[News, NewsCreate, NewsUpdate]):
    """CRUD operations for news articles"""

    def get_by_slug(self, session: Session, *, slug: str) -> Optional[News]:
        """Get news by slug"""
        statement = select(News).where(News.slug == slug)
        return session.exec(statement).first()

    def get_published_by_slug(self, session: Session, *, slug: str) -> Optional[News]:
        """Get published news by slug"""
        statement = select(News).where(
            and_(News.slug == slug, News.status == NewsStatus.published)
        )
        return session.exec(statement).first()

    def get_published_news(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[uuid.UUID] = None,
        source_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        is_breaking: Optional[bool] = None,
        priority: Optional[NewsPriority] = None,
    ) -> List[News]:
        """Get published news with optional filtering"""
        statement = select(News).where(News.status == NewsStatus.published)

        if category_id:
            statement = statement.where(News.category_id == category_id)

        if source_id:
            statement = statement.where(News.source_id == source_id)

        if user_id:
            statement = statement.where(News.user_id == user_id)

        if is_breaking is not None:
            statement = statement.where(News.is_breaking_news == is_breaking)

        if priority:
            statement = statement.where(News.priority == priority)

        statement = statement.order_by(News.published_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_breaking_news(
        self, session: Session, *, skip: int = 0, limit: int = 20
    ) -> List[News]:
        """Get breaking news articles"""
        statement = (
            select(News)
            .where(
                and_(News.status == NewsStatus.published, News.is_breaking_news == True)
            )
            .order_by(News.published_at.desc())
        )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_trending_news(
        self, session: Session, *, hours: int = 24, skip: int = 0, limit: int = 50
    ) -> List[News]:
        """Get trending news based on engagement"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)

        statement = (
            select(News)
            .where(
                and_(
                    News.status == NewsStatus.published,
                    News.published_at >= time_threshold,
                )
            )
            .order_by(
                (News.view_count + News.like_count * 2 + News.share_count * 3).desc()
            )
        )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_scheduled_news(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[News]:
        """Get scheduled news articles"""
        statement = (
            select(News)
            .where(
                and_(
                    News.status == NewsStatus.scheduled,
                    News.scheduled_at > datetime.utcnow(),
                )
            )
            .order_by(News.scheduled_at.asc())
        )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_by_category(
        self,
        session: Session,
        *,
        category_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        only_published: bool = True,
    ) -> List[News]:
        """Get news by category"""
        statement = select(News).where(News.category_id == category_id)

        if only_published:
            statement = statement.where(News.status == NewsStatus.published)

        statement = statement.order_by(News.published_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_by_source(
        self,
        session: Session,
        *,
        source_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        only_published: bool = True,
    ) -> List[News]:
        """Get news by source"""
        statement = select(News).where(News.source_id == source_id)

        if only_published:
            statement = statement.where(News.status == NewsStatus.published)

        statement = statement.order_by(News.published_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def search_news(
        self,
        session: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 50,
        only_published: bool = True,
    ) -> List[News]:
        """Search news by title, content, or summary"""
        search_term = f"%{query}%"

        statement = select(News).where(
            or_(
                News.title.ilike(search_term),
                News.content.ilike(search_term),
                News.summary.ilike(search_term),
                News.excerpt.ilike(search_term),
            )
        )

        if only_published:
            statement = statement.where(News.status == NewsStatus.published)

        statement = statement.order_by(
            case(
                (News.title.ilike(search_term), 1),
                (News.excerpt.ilike(search_term), 2),
                (News.summary.ilike(search_term), 3),
                else_=4,
            )
        ).order_by(News.published_at.desc())

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_news_by_location(
        self,
        session: Session,
        *,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[News]:
        """Get news by location"""
        statement = select(News).where(News.status == NewsStatus.published)

        if country:
            statement = statement.where(News.country.ilike(f"%{country}%"))

        if state:
            statement = statement.where(News.state.ilike(f"%{state}%"))

        if city:
            statement = statement.where(News.city.ilike(f"%{city}%"))

        statement = statement.order_by(News.published_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_user_news(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[NewsStatus] = None,
    ) -> List[News]:
        """Get news by user"""
        statement = select(News).where(News.user_id == user_id)

        if status:
            statement = statement.where(News.status == status)

        statement = statement.order_by(News.created_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_draft_news(self, session: Session, *, user_id: uuid.UUID) -> List[News]:
        """Get user's draft news"""
        statement = (
            select(News)
            .where(and_(News.user_id == user_id, News.status == NewsStatus.draft))
            .order_by(News.created_at.desc())
        )

        return list(session.exec(statement))

    def update_engagement_metrics(
        self, session: Session, *, news_id: uuid.UUID
    ) -> Optional[News]:
        """Update engagement metrics for news"""
        news = self.get(session=session, id=news_id)
        if not news:
            return None

        # Update last interaction time
        news.last_interaction_at = datetime.utcnow()

        session.add(news)
        session.commit()
        session.refresh(news)

        return news

    def schedule_news(
        self, session: Session, *, news_id: uuid.UUID, scheduled_at: datetime
    ) -> Optional[News]:
        """Schedule news for future publication"""
        news = self.get(session=session, id=news_id)
        if not news:
            return None

        news.status = NewsStatus.scheduled
        news.scheduled_at = scheduled_at

        session.add(news)
        session.commit()
        session.refresh(news)

        return news

    def publish_news(self, session: Session, *, news_id: uuid.UUID) -> Optional[News]:
        """Publish news"""
        news = self.get(session=session, id=news_id)
        if not news:
            return None

        news.status = NewsStatus.published
        news.published_at = datetime.utcnow()
        news.last_interaction_at = datetime.utcnow()

        session.add(news)
        session.commit()
        session.refresh(news)

        return news

    def archive_news(self, session: Session, *, news_id: uuid.UUID) -> Optional[News]:
        """Archive news"""
        news = self.get(session=session, id=news_id)
        if not news:
            return None

        news.status = NewsStatus.archived
        news.archived_at = datetime.utcnow()

        session.add(news)
        session.commit()
        session.refresh(news)

        return news

    def get_news_stats(
        self, session: Session, *, user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get news statistics"""
        base_query = select(News)

        if user_id:
            base_query = base_query.where(News.user_id == user_id)

        # Total news
        total_news = session.exec(
            select(func.count(News.id)).select_from(base_query)
        ).one()

        # By status
        published_count = session.exec(
            select(func.count(News.id))
            .select_from(base_query)
            .where(News.status == NewsStatus.published)
        ).one()

        draft_count = session.exec(
            select(func.count(News.id))
            .select_from(base_query)
            .where(News.status == NewsStatus.draft)
        ).one()

        scheduled_count = session.exec(
            select(func.count(News.id))
            .select_from(base_query)
            .where(News.status == NewsStatus.scheduled)
        ).one()

        # Breaking news
        breaking_count = session.exec(
            select(func.count(News.id))
            .select_from(base_query)
            .where(News.is_breaking_news == True)
        ).one()

        # Featured news
        featured_count = session.exec(
            select(func.count(News.id))
            .select_from(base_query)
            .where(News.is_featured == True)
        ).one()

        return {
            "total_news": total_news,
            "published_news": published_count,
            "draft_news": draft_count,
            "scheduled_news": scheduled_count,
            "breaking_news": breaking_count,
            "featured_news": featured_count,
        }

    def get_trending_topics(
        self, session: Session, *, days: int = 7, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get trending topics based on news engagement"""
        time_threshold = datetime.utcnow() - timedelta(days=days)

        # This is a simplified implementation
        # In production, you'd use more sophisticated algorithms
        statement = (
            select(News)
            .where(
                and_(
                    News.status == NewsStatus.published,
                    News.published_at >= time_threshold,
                )
            )
            .order_by(
                (News.view_count + News.like_count * 2 + News.share_count * 3).desc()
            )
            .limit(limit)
        )

        trending_news = session.exec(statement).all()

        topics = []
        for news in trending_news:
            topics.append(
                {
                    "id": news.id,
                    "title": news.title,
                    "slug": news.slug,
                    "engagement_score": news.view_count
                    + news.like_count * 2
                    + news.share_count * 3,
                    "view_count": news.view_count,
                    "like_count": news.like_count,
                    "share_count": news.share_count,
                    "published_at": news.published_at,
                }
            )

        return topics


# Create singleton instance
news = CRUDNews(News)
