from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Session

from app.modules.analytics.crud.analytics_crud import (
    crud_content_analytics,
    crud_platform_analytics,
    crud_user_analytics,
)
from app.modules.analytics.model.analytics import (
    ContentAnalytics,
    PlatformAnalytics,
    UserAnalytics,
)
from app.modules.analytics.schema.analytics import (
    AnalyticsSummary,
    ContentAnalyticsList,
    ContentAnalyticsPublic,
    DateRangeFilter,
    PlatformAnalyticsList,
    PlatformAnalyticsPublic,
    UserAnalyticsList,
    UserAnalyticsPublic,
)


class UserAnalyticsService:
    """Service layer for user analytics operations."""

    @staticmethod
    def get_user_analytics(
        session: Session, user_id: str, date_range: Optional[DateRangeFilter] = None
    ) -> UserAnalyticsList:
        """Get analytics for a specific user."""
        if date_range:
            analytics = crud_user_analytics.get_user_analytics_range(
                session, user_id, date_range.start_date, date_range.end_date
            )
        else:
            # Get last 30 days by default
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            analytics = crud_user_analytics.get_user_analytics_range(
                session, user_id, start_date, end_date
            )

        return UserAnalyticsList(
            data=[
                UserAnalyticsPublic.model_validate(analytic) for analytic in analytics
            ],
            total=len(analytics),
            user_id=user_id,
        )

    @staticmethod
    def get_user_analytics_summary(session: Session, user_id: str) -> Dict[str, Any]:
        """Get a summary of user analytics."""
        latest = crud_user_analytics.get_latest_user_analytics(session, user_id)

        if not latest:
            return {
                "profile_views": 0,
                "follower_count": 0,
                "total_posts": 0,
                "avg_engagement_rate": 0.0,
                "total_earnings": 0.0,
            }

        return {
            "profile_views": latest.profile_views,
            "follower_count": latest.follower_count,
            "total_posts": latest.total_posts,
            "avg_engagement_rate": latest.avg_engagement_rate,
            "total_earnings": latest.total_earnings,
            "last_updated": latest.date_recorded,
        }

    @staticmethod
    def update_user_analytics(
        session: Session, user_id: str, metrics: Dict[str, Any]
    ) -> UserAnalytics:
        """Update user analytics with new metrics."""
        return crud_user_analytics.update_user_metrics(session, user_id, metrics)


class ContentAnalyticsService:
    """Service layer for content analytics operations."""

    @staticmethod
    def get_content_analytics(
        session: Session, content_id: str, date_range: Optional[DateRangeFilter] = None
    ) -> ContentAnalyticsList:
        """Get analytics for specific content."""
        if date_range:
            analytics = crud_content_analytics.get_content_analytics_range(
                session, content_id, date_range.start_date, date_range.end_date
            )
        else:
            # Get last 7 days by default
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            analytics = crud_content_analytics.get_content_analytics_range(
                session, content_id, start_date, end_date
            )

        # Get content info from first analytics record
        content_type = analytics[0].content_type if analytics else None
        author_id = analytics[0].author_id if analytics else None

        return ContentAnalyticsList(
            data=[
                ContentAnalyticsPublic.model_validate(analytic)
                for analytic in analytics
            ],
            total=len(analytics),
            content_type=content_type,
            author_id=author_id,
        )

    @staticmethod
    def get_author_content_analytics(
        session: Session, author_id: str, content_type: Optional[str] = None
    ) -> ContentAnalyticsList:
        """Get all content analytics for an author."""
        analytics = crud_content_analytics.get_author_content_analytics(
            session, author_id, content_type
        )

        return ContentAnalyticsList(
            data=[
                ContentAnalyticsPublic.model_validate(analytic)
                for analytic in analytics
            ],
            total=len(analytics),
            author_id=author_id,
            content_type=content_type,
        )

    @staticmethod
    def get_top_performing_content(
        session: Session, content_type: Optional[str] = None, limit: int = 10
    ) -> List[ContentAnalytics]:
        """Get top performing content."""
        return crud_content_analytics.get_top_performing_content(
            session, content_type, limit
        )

    @staticmethod
    def update_content_analytics(
        session: Session, content_id: str, metrics: Dict[str, Any]
    ) -> ContentAnalytics:
        """Update content analytics with new metrics."""
        return crud_content_analytics.update_content_metrics(
            session, content_id, metrics
        )


class PlatformAnalyticsService:
    """Service layer for platform analytics operations."""

    @staticmethod
    def get_platform_analytics(
        session: Session, date_range: Optional[DateRangeFilter] = None
    ) -> PlatformAnalyticsList:
        """Get platform-wide analytics."""
        if date_range:
            analytics = crud_platform_analytics.get_platform_analytics_range(
                session, date_range.start_date, date_range.end_date
            )
        else:
            # Get last 30 days by default
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            analytics = crud_platform_analytics.get_platform_analytics_range(
                session, start_date, end_date
            )

        return PlatformAnalyticsList(
            data=[
                PlatformAnalyticsPublic.model_validate(analytic)
                for analytic in analytics
            ],
            total=len(analytics),
        )

    @staticmethod
    def get_platform_summary(session: Session) -> AnalyticsSummary:
        """Get a summary of platform analytics."""
        latest = crud_platform_analytics.get_latest_platform_analytics(session)

        if not latest:
            return AnalyticsSummary(
                total_users=0,
                active_users_today=0,
                total_content=0,
                total_engagement=0,
                top_performing_content=[],
                user_growth_trend=[],
            )

        # Get top performing content
        top_content = crud_content_analytics.get_top_performing_content(
            session, limit=5
        )

        return AnalyticsSummary(
            total_users=latest.total_users,
            active_users_today=latest.active_users_daily,
            total_content=latest.total_posts
            + latest.total_stories
            + latest.total_reels
            + latest.total_news_articles,
            total_engagement=latest.total_likes
            + latest.total_comments
            + latest.total_shares,
            top_performing_content=[
                {
                    "content_id": content.content_id,
                    "content_type": content.content_type,
                    "performance_score": content.performance_score,
                    "views": content.views,
                    "engagement_rate": content.engagement_rate,
                }
                for content in top_content
            ],
            user_growth_trend=[],  # Would need historical data
            revenue_trend=None,  # Would need monetization data
        )

    @staticmethod
    def update_platform_analytics(
        session: Session, metrics: Dict[str, Any]
    ) -> PlatformAnalytics:
        """Update platform analytics with new metrics."""
        return crud_platform_analytics.update_platform_metrics(session, metrics)


# Service instances
user_analytics_service = UserAnalyticsService()
content_analytics_service = ContentAnalyticsService()
platform_analytics_service = PlatformAnalyticsService()
