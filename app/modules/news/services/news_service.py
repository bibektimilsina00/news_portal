import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from app.modules.news.crud.crud_news import news
from app.modules.news.model.news import News, NewsPriority, NewsStatus
from app.modules.news.schema.news import (
    NewsCreate,
    NewsFilter,
    NewsUpdate,
)
from app.shared.exceptions.exceptions import (
    PostNotFoundException,
    UnauthorizedException,
)


class NewsService:
    """Service layer for news management"""

    @staticmethod
    def create_news(
        *, session: Session, news_create: NewsCreate, current_user_id: uuid.UUID
    ) -> News:
        """Create new news article"""
        # Generate slug from title if not provided
        if not news_create.slug:
            news_create.slug = (
                news_create.title.lower().replace(" ", "-").replace("/", "-")
            )

        # Set user_id
        news_create.user_id = current_user_id

        return news.create(session=session, obj_in=news_create)

    @staticmethod
    def get_news(
        session: Session,
        news_id: uuid.UUID,
        current_user_id: Optional[uuid.UUID] = None,
    ) -> Optional[News]:
        """Get news article by ID"""
        news_obj = news.get(session=session, id=news_id)
        if not news_obj:
            return None

        # Check visibility permissions
        if news_obj.visibility == "private" and news_obj.user_id != current_user_id:
            return None

        return news_obj

    @staticmethod
    def get_news_by_slug(session: Session, slug: str) -> Optional[News]:
        """Get news article by slug"""
        return session.exec(select(News).where(News.slug == slug)).first()

    @staticmethod
    def get_news_list(
        session: Session,
        skip: int = 0,
        limit: int = 20,
        news_filter: Optional[NewsFilter] = None,
        current_user_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Get list of news articles with filtering"""
        query = select(News)

        # Apply filters
        if news_filter:
            if news_filter.status:
                query = query.where(News.status == news_filter.status)
            if news_filter.category_id:
                query = query.where(News.category_id == news_filter.category_id)
            if news_filter.source_id:
                query = query.where(News.source_id == news_filter.source_id)
            if news_filter.priority:
                query = query.where(News.priority == news_filter.priority)
            if news_filter.is_breaking_news is not None:
                query = query.where(
                    News.is_breaking_news == news_filter.is_breaking_news
                )
            if news_filter.is_featured is not None:
                query = query.where(News.is_featured == news_filter.is_featured)
            if news_filter.location_name:
                query = query.where(
                    News.location_name.ilike(f"%{news_filter.location_name}%")
                )
            if news_filter.search_query:
                search_term = f"%{news_filter.search_query}%"
                query = query.where(
                    (News.title.ilike(search_term))
                    | (News.content.ilike(search_term))
                    | (News.summary.ilike(search_term))
                )

        # Only show published news to non-owners
        if current_user_id:
            query = query.where(
                (News.status == NewsStatus.published)
                | (News.user_id == current_user_id)
            )
        else:
            query = query.where(News.status == NewsStatus.published)

        # Apply sorting
        sort_field = getattr(News, news_filter.sort_by if news_filter else "created_at")
        if news_filter and news_filter.sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        # Get total count
        total_count = len(session.exec(query).all())

        # Apply pagination
        news_items = session.exec(query.offset(skip).limit(limit)).all()

        return {
            "items": news_items,
            "total": total_count,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    def get_user_news(
        session: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[NewsStatus] = None,
    ) -> Dict[str, Any]:
        """Get news articles by user"""
        query = select(News).where(News.user_id == user_id)

        if status:
            query = query.where(News.status == status)

        query = query.order_by(News.created_at.desc())

        total_count = len(session.exec(query).all())
        news_items = session.exec(query.offset(skip).limit(limit)).all()

        return {
            "items": news_items,
            "total": total_count,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    def update_news(
        session: Session,
        news_id: uuid.UUID,
        news_update: NewsUpdate,
        current_user_id: uuid.UUID,
    ) -> News:
        """Update news article"""
        news_obj = news.get(session=session, id=news_id)
        if not news_obj:
            raise PostNotFoundException("News article not found")

        if news_obj.user_id != current_user_id:
            raise UnauthorizedException("Not authorized to update this news article")

        return news.update(session=session, db_obj=news_obj, obj_in=news_update)

    @staticmethod
    def delete_news(
        session: Session, news_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> News:
        """Delete news article"""
        news_obj = news.get(session=session, id=news_id)
        if not news_obj:
            raise PostNotFoundException("News article not found")

        if news_obj.user_id != current_user_id:
            raise UnauthorizedException("Not authorized to delete this news article")

        return news.remove(session=session, id=news_id)

    @staticmethod
    def publish_news(
        session: Session, news_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> News:
        """Publish draft news article"""
        news_obj = news.get(session=session, id=news_id)
        if not news_obj:
            raise PostNotFoundException("News article not found")

        if news_obj.user_id != current_user_id:
            raise UnauthorizedException("Not authorized to publish this news article")

        if news_obj.status != NewsStatus.draft:
            raise Exception("Only draft articles can be published")

        update_data = NewsUpdate(
            status=NewsStatus.published, published_at=datetime.utcnow()
        )
        return news.update(session=session, db_obj=news_obj, obj_in=update_data)

    @staticmethod
    def schedule_news(
        session: Session,
        news_id: uuid.UUID,
        scheduled_at: datetime,
        current_user_id: uuid.UUID,
    ) -> News:
        """Schedule news article for future publication"""
        news_obj = news.get(session=session, id=news_id)
        if not news_obj:
            raise PostNotFoundException("News article not found")

        if news_obj.user_id != current_user_id:
            raise UnauthorizedException("Not authorized to schedule this news article")

        if scheduled_at <= datetime.utcnow():
            raise Exception("Scheduled time must be in the future")

        update_data = NewsUpdate(status=NewsStatus.scheduled, scheduled_at=scheduled_at)
        return news.update(session=session, db_obj=news_obj, obj_in=update_data)

    @staticmethod
    def mark_as_breaking(
        session: Session, news_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> News:
        """Mark news article as breaking news"""
        news_obj = news.get(session=session, id=news_id)
        if not news_obj:
            raise PostNotFoundException("News article not found")

        if news_obj.user_id != current_user_id:
            raise UnauthorizedException("Not authorized to modify this news article")

        update_data = NewsUpdate(is_breaking_news=True, priority=NewsPriority.breaking)
        return news.update(session=session, db_obj=news_obj, obj_in=update_data)

    @staticmethod
    def mark_as_featured(
        session: Session, news_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> News:
        """Mark news article as featured"""
        news_obj = news.get(session=session, id=news_id)
        if not news_obj:
            raise PostNotFoundException("News article not found")

        if news_obj.user_id != current_user_id:
            raise UnauthorizedException("Not authorized to modify this news article")

        update_data = NewsUpdate(is_featured=True)
        return news.update(session=session, db_obj=news_obj, obj_in=update_data)

    @staticmethod
    def get_trending_news(
        session: Session, limit: int = 10, hours: int = 24
    ) -> List[News]:
        """Get trending news based on view count"""
        # This would typically use a more sophisticated algorithm
        # For now, just return most viewed news in the last N hours
        cutoff_time = datetime.utcnow()  # Would need to calculate based on hours

        query = (
            select(News)
            .where(News.status == NewsStatus.published)
            .where(News.created_at >= cutoff_time)
            .order_by(News.view_count.desc())
            .limit(limit)
        )

        return session.exec(query).all()

    @staticmethod
    def increment_view_count(session: Session, news_id: uuid.UUID) -> None:
        """Increment view count for news article"""
        news_obj = news.get(session=session, id=news_id)
        if news_obj:
            update_data = NewsUpdate(view_count=news_obj.view_count + 1)
            news.update(session=session, db_obj=news_obj, obj_in=update_data)

    @staticmethod
    def get_news_stats(
        session: Session, user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get news statistics"""
        query = select(News)

        if user_id:
            query = query.where(News.user_id == user_id)

        all_news = session.exec(query).all()

        stats = {
            "total_news": len(all_news),
            "published": len([n for n in all_news if n.status == NewsStatus.published]),
            "drafts": len([n for n in all_news if n.status == NewsStatus.draft]),
            "scheduled": len([n for n in all_news if n.status == NewsStatus.scheduled]),
            "breaking_news": len([n for n in all_news if n.is_breaking_news]),
            "featured": len([n for n in all_news if n.is_featured]),
            "total_views": sum(n.view_count for n in all_news),
            "avg_credibility_score": (
                sum(n.credibility_score for n in all_news if n.credibility_score)
                / len([n for n in all_news if n.credibility_score])
                if any(n.credibility_score for n in all_news)
                else 0
            ),
        }

        return stats


# Create singleton instance
news_service = NewsService()
