from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.modules.analytics.schema.analytics import (
    AnalyticsSummary,
    ContentAnalyticsList,
    ContentAnalyticsPublic,
    DateRangeFilter,
    PlatformAnalyticsList,
    UserAnalyticsList,
)
from app.modules.analytics.services.analytics_service import (
    content_analytics_service,
    platform_analytics_service,
    user_analytics_service,
)
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/me", response_model=UserAnalyticsList)
def get_my_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    granularity: str = Query("daily", description="daily, weekly, or monthly"),
) -> UserAnalyticsList:
    """
    Get analytics for the current user.
    """
    from datetime import datetime

    date_range = None
    if start_date and end_date:
        date_range = DateRangeFilter(
            start_date=datetime.fromisoformat(start_date),
            end_date=datetime.fromisoformat(end_date),
            granularity=granularity,
        )

    return user_analytics_service.get_user_analytics(
        session, str(current_user.id), date_range
    )


@router.get("/me/summary")
def get_my_analytics_summary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """
    Get a summary of analytics for the current user.
    """
    return user_analytics_service.get_user_analytics_summary(
        session, str(current_user.id)
    )


@router.get("/content/{content_id}", response_model=ContentAnalyticsList)
def get_content_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
) -> ContentAnalyticsList:
    """
    Get analytics for specific content.
    """
    from datetime import datetime

    date_range = None
    if start_date and end_date:
        date_range = DateRangeFilter(
            start_date=datetime.fromisoformat(start_date),
            end_date=datetime.fromisoformat(end_date),
        )

    return content_analytics_service.get_content_analytics(
        session, content_id, date_range
    )


@router.get("/author/{author_id}", response_model=ContentAnalyticsList)
def get_author_content_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    author_id: str,
    content_type: Optional[str] = Query(None, description="Filter by content type"),
) -> ContentAnalyticsList:
    """
    Get all content analytics for an author.
    """
    return content_analytics_service.get_author_content_analytics(
        session, author_id, content_type
    )


@router.get("/top-content", response_model=List[ContentAnalyticsPublic])
def get_top_performing_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    limit: int = Query(10, ge=1, le=50),
) -> List[ContentAnalyticsPublic]:
    """
    Get top performing content.
    """
    content = content_analytics_service.get_top_performing_content(
        session, content_type, limit
    )
    return [ContentAnalyticsPublic.model_validate(c) for c in content]


@router.get("/platform", response_model=PlatformAnalyticsList)
def get_platform_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
) -> PlatformAnalyticsList:
    """
    Get platform-wide analytics (admin only).
    """
    # TODO: Add admin check
    from datetime import datetime

    date_range = None
    if start_date and end_date:
        date_range = DateRangeFilter(
            start_date=datetime.fromisoformat(start_date),
            end_date=datetime.fromisoformat(end_date),
        )

    return platform_analytics_service.get_platform_analytics(session, date_range)


@router.get("/platform/summary", response_model=AnalyticsSummary)
def get_platform_summary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> AnalyticsSummary:
    """
    Get platform analytics summary (admin only).
    """
    # TODO: Add admin check
    return platform_analytics_service.get_platform_summary(session)


@router.post("/track/user/{user_id}")
def track_user_analytics(
    *, session: SessionDep, current_user: CurrentUser, user_id: str, metrics: dict
) -> dict:
    """
    Track user analytics metrics (internal use).
    """
    # TODO: Add proper authorization check
    analytics = user_analytics_service.update_user_analytics(session, user_id, metrics)
    return {"message": "User analytics updated", "id": analytics.id}


@router.post("/track/content/{content_id}")
def track_content_analytics(
    *, session: SessionDep, current_user: CurrentUser, content_id: str, metrics: dict
) -> dict:
    """
    Track content analytics metrics (internal use).
    """
    # TODO: Add proper authorization check
    analytics = content_analytics_service.update_content_analytics(
        session, content_id, metrics
    )
    return {"message": "Content analytics updated", "id": analytics.id}


@router.post("/track/platform")
def track_platform_analytics(
    *, session: SessionDep, current_user: CurrentUser, metrics: dict
) -> dict:
    """
    Track platform analytics metrics (admin only).
    """
    # TODO: Add admin check
    analytics = platform_analytics_service.update_platform_analytics(session, metrics)
    return {"message": "Platform analytics updated", "id": analytics.id}
