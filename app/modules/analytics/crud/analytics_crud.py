from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Session, desc, select

from app.modules.analytics.model.analytics import (
    ContentAnalytics,
    PlatformAnalytics,
    UserAnalytics,
)
from app.shared.crud.base import CRUDBase


class CRUDUserAnalytics(CRUDBase[UserAnalytics, UserAnalytics, UserAnalytics]):
    def get_by_user_and_date(
        self, session: Session, user_id: str, date: datetime
    ) -> Optional[UserAnalytics]:
        """Get user analytics for a specific date."""
        return session.exec(
            select(UserAnalytics).where(
                UserAnalytics.user_id == user_id,
                UserAnalytics.date_recorded
                >= date.replace(hour=0, minute=0, second=0, microsecond=0),
                UserAnalytics.date_recorded
                < (date + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
            )
        ).first()

    def get_user_analytics_range(
        self, session: Session, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[UserAnalytics]:
        """Get user analytics for a date range."""
        return list(
            session.exec(
                select(UserAnalytics)
                .where(
                    UserAnalytics.user_id == user_id,
                    UserAnalytics.date_recorded >= start_date,
                    UserAnalytics.date_recorded <= end_date,
                )
                .order_by(UserAnalytics.date_recorded)
            )
        )

    def get_latest_user_analytics(
        self, session: Session, user_id: str
    ) -> Optional[UserAnalytics]:
        """Get the most recent analytics for a user."""
        return session.exec(
            select(UserAnalytics)
            .where(UserAnalytics.user_id == user_id)
            .order_by(desc(UserAnalytics.date_recorded))
            .limit(1)
        ).first()

    def update_user_metrics(
        self, session: Session, user_id: str, metrics: Dict[str, Any]
    ) -> UserAnalytics:
        """Update or create user analytics for today."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Try to get existing analytics for today
        analytics = self.get_by_user_and_date(session, user_id, today)

        if analytics:
            # Update existing
            for key, value in metrics.items():
                if hasattr(analytics, key):
                    setattr(analytics, key, value)
            analytics.date_recorded = datetime.utcnow()
            session.add(analytics)
            session.commit()
            session.refresh(analytics)
            return analytics
        else:
            # Create new
            analytics_data = {
                "user_id": user_id,
                "date_recorded": datetime.utcnow(),
                "week_start": week_start,
                "month_start": month_start,
                **metrics,
            }
            return self.create(session, obj_in=UserAnalytics(**analytics_data))


class CRUDContentAnalytics(
    CRUDBase[ContentAnalytics, ContentAnalytics, ContentAnalytics]
):
    def get_by_content_and_date(
        self, session: Session, content_id: str, date: datetime
    ) -> Optional[ContentAnalytics]:
        """Get content analytics for a specific date."""
        return session.exec(
            select(ContentAnalytics).where(
                ContentAnalytics.content_id == content_id,
                ContentAnalytics.date_recorded
                >= date.replace(hour=0, minute=0, second=0, microsecond=0),
                ContentAnalytics.date_recorded
                < (date + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
            )
        ).first()

    def get_content_analytics_range(
        self,
        session: Session,
        content_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[ContentAnalytics]:
        """Get content analytics for a date range."""
        return list(
            session.exec(
                select(ContentAnalytics)
                .where(
                    ContentAnalytics.content_id == content_id,
                    ContentAnalytics.date_recorded >= start_date,
                    ContentAnalytics.date_recorded <= end_date,
                )
                .order_by(ContentAnalytics.date_recorded)
            )
        )

    def get_top_performing_content(
        self, session: Session, content_type: Optional[str] = None, limit: int = 10
    ) -> List[ContentAnalytics]:
        """Get top performing content by engagement rate."""
        query = (
            select(ContentAnalytics)
            .order_by(desc(ContentAnalytics.performance_score))
            .limit(limit)
        )

        if content_type:
            query = query.where(ContentAnalytics.content_type == content_type)

        return list(session.exec(query))

    def get_author_content_analytics(
        self, session: Session, author_id: str, content_type: Optional[str] = None
    ) -> List[ContentAnalytics]:
        """Get all content analytics for an author."""
        query = select(ContentAnalytics).where(ContentAnalytics.author_id == author_id)

        if content_type:
            query = query.where(ContentAnalytics.content_type == content_type)

        return list(session.exec(query.order_by(desc(ContentAnalytics.date_recorded))))

    def update_content_metrics(
        self, session: Session, content_id: str, metrics: Dict[str, Any]
    ) -> ContentAnalytics:
        """Update or create content analytics for today."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Try to get existing analytics for today
        analytics = self.get_by_content_and_date(session, content_id, today)

        if analytics:
            # Update existing
            for key, value in metrics.items():
                if hasattr(analytics, key):
                    setattr(analytics, key, value)
            analytics.date_recorded = datetime.utcnow()
            session.add(analytics)
            session.commit()
            session.refresh(analytics)
            return analytics
        else:
            # Create new - need content_type and author_id from metrics
            analytics_data = {
                "content_id": content_id,
                "date_recorded": datetime.utcnow(),
                "content_created_at": datetime.utcnow(),  # This should be passed in metrics
                **metrics,
            }
            return self.create(session, obj_in=ContentAnalytics(**analytics_data))


class CRUDPlatformAnalytics(
    CRUDBase[PlatformAnalytics, PlatformAnalytics, PlatformAnalytics]
):
    def get_latest_platform_analytics(
        self, session: Session
    ) -> Optional[PlatformAnalytics]:
        """Get the most recent platform analytics."""
        return session.exec(
            select(PlatformAnalytics)
            .order_by(desc(PlatformAnalytics.date_recorded))
            .limit(1)
        ).first()

    def get_platform_analytics_range(
        self, session: Session, start_date: datetime, end_date: datetime
    ) -> List[PlatformAnalytics]:
        """Get platform analytics for a date range."""
        return list(
            session.exec(
                select(PlatformAnalytics)
                .where(
                    PlatformAnalytics.date_recorded >= start_date,
                    PlatformAnalytics.date_recorded <= end_date,
                )
                .order_by(PlatformAnalytics.date_recorded)
            )
        )

    def update_platform_metrics(
        self, session: Session, metrics: Dict[str, Any]
    ) -> PlatformAnalytics:
        """Update platform analytics for today."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Try to get existing analytics for today
        analytics = session.exec(
            select(PlatformAnalytics)
            .where(
                PlatformAnalytics.date_recorded >= today,
                PlatformAnalytics.date_recorded < today + timedelta(days=1),
            )
            .limit(1)
        ).first()

        if analytics:
            # Update existing
            for key, value in metrics.items():
                if hasattr(analytics, key):
                    setattr(analytics, key, value)
            analytics.date_recorded = datetime.utcnow()
            session.add(analytics)
            session.commit()
            session.refresh(analytics)
            return analytics
        else:
            # Create new
            analytics_data = {
                "date_recorded": datetime.utcnow(),
                "week_start": week_start,
                "month_start": month_start,
                **metrics,
            }
            return self.create(session, obj_in=PlatformAnalytics(**analytics_data))


crud_user_analytics = CRUDUserAnalytics(UserAnalytics)
crud_content_analytics = CRUDContentAnalytics(ContentAnalytics)
crud_platform_analytics = CRUDPlatformAnalytics(PlatformAnalytics)
