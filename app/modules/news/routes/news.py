import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.modules.news.model.news import NewsStatus
from app.modules.news.schema.news import (
    BreakingNewsResponse,
    NewsByLocationResponse,
    NewsCreate,
    NewsFilter,
    NewsListResponse,
    NewsPublishRequest,
    NewsPublishResponse,
    NewsResponse,
    NewsScheduleRequest,
    NewsSearchResponse,
    NewsStats,
    NewsUpdate,
    TrendingNewsResponse,
)
from app.modules.news.services.news_service import news_service
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.exceptions.exceptions import (
    PostNotFoundException,
    UnauthorizedException,
)
from app.shared.schema.message import Message

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/", response_model=NewsListResponse)
def get_news(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    news_filter: NewsFilter = Depends(),
) -> Any:
    """
    Get news articles with filtering and pagination
    """
    try:
        result = news_service.get_news_list(
            session=session,
            skip=skip,
            limit=limit,
            news_filter=news_filter,
            current_user_id=current_user.id,
        )

        return NewsListResponse(
            news=result["items"],
            total=result["total"],
            page=(skip // limit) + 1,
            per_page=limit,
            has_next=(skip + limit) < result["total"],
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news: {str(e)}",
        )


@router.get("/breaking", response_model=BreakingNewsResponse)
def get_breaking_news(
    session: SessionDep,
    limit: int = Query(10, ge=1, le=50),
) -> Any:
    """
    Get breaking news articles
    """
    try:
        # Get news marked as breaking
        news_filter = NewsFilter(is_breaking_news=True, status=NewsStatus.published)
        result = news_service.get_news_list(
            session=session, skip=0, limit=limit, news_filter=news_filter
        )

        return BreakingNewsResponse(
            breaking_news=result["items"],
            total=result["total"],
            last_updated=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve breaking news: {str(e)}",
        )


@router.get("/trending", response_model=TrendingNewsResponse)
def get_trending_news(
    session: SessionDep,
    limit: int = Query(10, ge=1, le=50),
    hours: int = Query(24, ge=1, le=168),
) -> Any:
    """
    Get trending news articles
    """
    try:
        trending_news = news_service.get_trending_news(
            session=session, limit=limit, hours=hours
        )

        return TrendingNewsResponse(
            trending_news=[NewsResponse.model_validate(news) for news in trending_news],
            total=len(trending_news),
            time_period=f"{hours} hours",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trending news: {str(e)}",
        )


@router.get("/featured", response_model=NewsListResponse)
def get_featured_news(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get featured news articles
    """
    try:
        news_filter = NewsFilter(is_featured=True, status=NewsStatus.published)
        result = news_service.get_news_list(
            session=session, skip=skip, limit=limit, news_filter=news_filter
        )

        return NewsListResponse(
            news=result["items"],
            total=result["total"],
            page=(skip // limit) + 1,
            per_page=limit,
            has_next=(skip + limit) < result["total"],
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve featured news: {str(e)}",
        )


@router.get("/me", response_model=NewsListResponse)
def get_my_news(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
) -> Any:
    """
    Get current user's news articles
    """
    try:
        status_enum = None
        if status_filter:
            from app.modules.news.model.news import NewsStatus

            status_enum = NewsStatus(status_filter)

        result = news_service.get_user_news(
            session=session,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=status_enum,
        )

        return NewsListResponse(
            news=result["items"],
            total=result["total"],
            page=(skip // limit) + 1,
            per_page=limit,
            has_next=(skip + limit) < result["total"],
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user news: {str(e)}",
        )


@router.get("/me/drafts", response_model=NewsListResponse)
def get_my_drafts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get current user's draft news articles
    """
    try:
        from app.modules.news.model.news import NewsStatus

        result = news_service.get_user_news(
            session=session,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=NewsStatus.draft,
        )

        return NewsListResponse(
            news=result["items"],
            total=result["total"],
            page=(skip // limit) + 1,
            per_page=limit,
            has_next=(skip + limit) < result["total"],
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve draft news: {str(e)}",
        )


@router.get("/me/scheduled", response_model=NewsListResponse)
def get_my_scheduled(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get current user's scheduled news articles
    """
    try:
        from app.modules.news.model.news import NewsStatus

        result = news_service.get_user_news(
            session=session,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=NewsStatus.scheduled,
        )

        return NewsListResponse(
            news=result["items"],
            total=result["total"],
            page=(skip // limit) + 1,
            per_page=limit,
            has_next=(skip + limit) < result["total"],
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scheduled news: {str(e)}",
        )


@router.get("/{news_id}", response_model=NewsResponse)
def get_news_by_id(
    session: SessionDep,
    news_id: uuid.UUID,
    current_user: CurrentUser,
) -> Any:
    """
    Get news article by ID
    """
    try:
        news_obj = news_service.get_news(
            session=session, news_id=news_id, current_user_id=current_user.id
        )
        if not news_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
            )

        # Increment view count
        news_service.increment_view_count(session=session, news_id=news_id)

        return news_obj
    except PostNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news article: {str(e)}",
        )


@router.get("/slug/{slug}", response_model=NewsResponse)
def get_news_by_slug(
    session: SessionDep,
    slug: str,
    current_user: CurrentUser,
) -> Any:
    """
    Get news article by slug
    """
    try:
        news_obj = news_service.get_news_by_slug(session=session, slug=slug)
        if not news_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
            )

        # Check visibility permissions
        if news_obj.visibility == "private" and news_obj.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this news article",
            )

        # Increment view count
        news_service.increment_view_count(session=session, news_id=news_obj.id)

        return news_obj
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news article: {str(e)}",
        )


@router.post("/", response_model=NewsResponse)
def create_news(
    session: SessionDep,
    news_in: NewsCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Create new news article
    """
    try:
        news_obj = news_service.create_news(
            session=session, news_create=news_in, current_user_id=current_user.id
        )
        return news_obj
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create news article: {str(e)}",
        )


@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    session: SessionDep,
    news_id: uuid.UUID,
    news_in: NewsUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update news article
    """
    try:
        news_obj = news_service.update_news(
            session=session,
            news_id=news_id,
            news_update=news_in,
            current_user_id=current_user.id,
        )
        return news_obj
    except PostNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
        )
    except UnauthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this news article",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update news article: {str(e)}",
        )


@router.delete("/{news_id}", response_model=Message)
def delete_news(
    session: SessionDep,
    news_id: uuid.UUID,
    current_user: CurrentUser,
) -> Any:
    """
    Delete news article
    """
    try:
        news_service.delete_news(
            session=session, news_id=news_id, current_user_id=current_user.id
        )
        return Message(message="News article deleted successfully")
    except PostNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
        )
    except UnauthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this news article",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete news article: {str(e)}",
        )


@router.post("/{news_id}/publish", response_model=NewsPublishResponse)
def publish_news(
    session: SessionDep,
    news_id: uuid.UUID,
    current_user: CurrentUser,
) -> Any:
    """
    Publish draft news article
    """
    try:
        news_obj = news_service.publish_news(
            session=session, news_id=news_id, current_user_id=current_user.id
        )
        return NewsPublishResponse(
            news_id=news_obj.id,
            status=news_obj.status,
            published_at=news_obj.published_at,
            message="News article published successfully",
        )
    except PostNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
        )
    except UnauthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this news article",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{news_id}/schedule", response_model=NewsResponse)
def schedule_news(
    session: SessionDep,
    news_id: uuid.UUID,
    schedule_request: NewsScheduleRequest,
    current_user: CurrentUser,
) -> Any:
    """
    Schedule news article for future publication
    """
    try:
        news_obj = news_service.schedule_news(
            session=session,
            news_id=news_id,
            scheduled_at=schedule_request.scheduled_at,
            current_user_id=current_user.id,
        )
        return news_obj
    except PostNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
        )
    except UnauthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to schedule this news article",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{news_id}/breaking", response_model=NewsResponse)
def mark_as_breaking(
    session: SessionDep,
    news_id: uuid.UUID,
    current_user: CurrentUser,
) -> Any:
    """
    Mark news article as breaking news
    """
    try:
        news_obj = news_service.mark_as_breaking(
            session=session, news_id=news_id, current_user_id=current_user.id
        )
        return news_obj
    except PostNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
        )
    except UnauthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this news article",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark as breaking news: {str(e)}",
        )


@router.post("/{news_id}/featured", response_model=NewsResponse)
def mark_as_featured(
    session: SessionDep,
    news_id: uuid.UUID,
    current_user: CurrentUser,
) -> Any:
    """
    Mark news article as featured
    """
    try:
        news_obj = news_service.mark_as_featured(
            session=session, news_id=news_id, current_user_id=current_user.id
        )
        return news_obj
    except PostNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
        )
    except UnauthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this news article",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark as featured: {str(e)}",
        )


@router.get("/search", response_model=NewsSearchResponse)
def search_news(
    session: SessionDep,
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[CurrentUser] = None,
) -> Any:
    """
    Search news articles
    """
    try:
        # For now, use the existing get_news_list with search filter
        news_filter = NewsFilter(search_query=q, status=NewsStatus.published)
        result = news_service.get_news_list(
            session=session,
            skip=skip,
            limit=limit,
            news_filter=news_filter,
            current_user_id=current_user.id if current_user else None,
        )

        return NewsSearchResponse(
            results=result["items"],
            total=result["total"],
            query=q,
            suggestions=[],  # Could implement search suggestions later
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search news: {str(e)}",
        )


@router.get("/location/nearby", response_model=NewsByLocationResponse)
def get_nearby_news(
    session: SessionDep,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10, ge=0.1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[CurrentUser] = None,
) -> Any:
    """
    Get news articles near a location
    """
    try:
        # For now, filter by location name or coordinates
        # A more sophisticated implementation would use geospatial queries
        news_filter = NewsFilter(status=NewsStatus.published)
        result = news_service.get_news_list(
            session=session,
            skip=skip,
            limit=limit,
            news_filter=news_filter,
            current_user_id=current_user.id if current_user else None,
        )

        # Filter results by location (simplified)
        nearby_news = [
            news_item
            for news_item in result["items"]
            if news_item.latitude and news_item.longitude
        ]

        return NewsByLocationResponse(
            location=f"{latitude},{longitude}",
            news=nearby_news,
            total=len(nearby_news),
            coordinates={"latitude": latitude, "longitude": longitude},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nearby news: {str(e)}",
        )


@router.get("/stats", response_model=NewsStats)
def get_news_stats(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get news statistics for current user
    """
    try:
        stats = news_service.get_news_stats(session=session, user_id=current_user.id)
        return NewsStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get news stats: {str(e)}",
        )
