from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.modules.search.model.trending import TrendingTopic
from app.modules.search.schema.trending import (
    TrendingTopicCreate,
    TrendingTopicPublic,
    TrendingTopicsList,
)
from app.modules.search.services.trending_service import trending_topic_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/", response_model=TrendingTopicsList)
def get_trending_topics(
    *,
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> TrendingTopicsList:
    """
    Get active trending topics.
    """
    return trending_topic_service.get_trending_topics_response(
        session, skip=skip, limit=limit
    )


@router.get("/category/{category}", response_model=List[TrendingTopicPublic])
def get_trending_topics_by_category(
    *,
    session: SessionDep,
    category: str,
    limit: int = Query(10, ge=1, le=50),
) -> List[TrendingTopic]:
    """
    Get trending topics for a specific category.
    """
    topics = trending_topic_service.get_trending_topics_by_category(
        session, category=category, limit=limit
    )
    return [TrendingTopicPublic.model_validate(topic) for topic in topics]


@router.get("/{topic_id}", response_model=TrendingTopicPublic)
def get_trending_topic(
    *,
    session: SessionDep,
    topic_id: str,
) -> TrendingTopic:
    """
    Get a specific trending topic by ID.
    """
    topic = trending_topic_service.get_trending_topic_by_id(session, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Trending topic not found")
    return TrendingTopicPublic.model_validate(topic)


@router.get("/search/{topic}", response_model=TrendingTopicPublic)
def get_trending_topic_by_name(
    *,
    session: SessionDep,
    topic: str,
) -> TrendingTopic:
    """
    Get a trending topic by name.
    """
    topic_obj = trending_topic_service.get_trending_topic_by_name(session, topic=topic)
    if not topic_obj:
        raise HTTPException(status_code=404, detail="Trending topic not found")
    return TrendingTopicPublic.model_validate(topic_obj)


@router.post("/", response_model=TrendingTopicPublic)
def create_trending_topic(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    topic_in: TrendingTopicCreate,
) -> TrendingTopic:
    """
    Create a new trending topic (admin only).
    """
    # TODO: Add admin check
    return TrendingTopicPublic.model_validate(
        trending_topic_service.create_trending_topic(session, topic_in)
    )


@router.put("/{topic_id}", response_model=TrendingTopicPublic)
def update_trending_topic(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    topic_id: str,
    topic_update: TrendingTopicCreate,  # Using Create for simplicity
) -> TrendingTopic:
    """
    Update a trending topic (admin only).
    """
    # TODO: Add admin check
    updated_topic = trending_topic_service.update_trending_topic(
        session, topic_id=topic_id, topic_update=topic_update
    )
    if not updated_topic:
        raise HTTPException(status_code=404, detail="Trending topic not found")
    return TrendingTopicPublic.model_validate(updated_topic)


@router.delete("/{topic_id}", response_model=TrendingTopicPublic)
def delete_trending_topic(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    topic_id: str,
) -> TrendingTopic:
    """
    Delete a trending topic (admin only).
    """
    # TODO: Add admin check
    deleted_topic = trending_topic_service.delete_trending_topic(
        session, topic_id=topic_id
    )
    if not deleted_topic:
        raise HTTPException(status_code=404, detail="Trending topic not found")
    return TrendingTopicPublic.model_validate(deleted_topic)


@router.post("/increment/{topic}", response_model=TrendingTopicPublic)
def increment_topic_engagement(
    *,
    session: SessionDep,
    topic: str,
    increment: float = Query(1.0, ge=0.1),
) -> TrendingTopic:
    """
    Increment engagement score for a topic (creates if doesn't exist).
    """
    return TrendingTopicPublic.model_validate(
        trending_topic_service.increment_topic_engagement(
            session, topic=topic, increment=increment
        )
    )


@router.post("/cleanup", response_model=dict)
def cleanup_expired_topics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    hours_old: int = Query(24, ge=1),
) -> dict:
    """
    Clean up expired trending topics (admin only).
    """
    # TODO: Add admin check
    cleaned_count = trending_topic_service.cleanup_expired_topics(
        session, hours_old=hours_old
    )
    return {"message": f"Cleaned up {cleaned_count} expired trending topics"}
