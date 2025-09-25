import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.modules.stories.schema.viewer import StoryViewerPublic, StoryViewerUpdate
from app.modules.stories.services.viewer_service import story_viewer_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/viewers", tags=["story-viewers"])


@router.get("/story/{story_id}", response_model=List[StoryViewerPublic])
def get_story_viewers(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get viewers for a specific story (story owner only)
    """
    # TODO: Check if current user owns the story
    # For now, allow any authenticated user

    viewers = story_viewer_service.get_story_viewers(
        session=session,
        story_id=story_id,
        skip=skip,
        limit=limit,
    )
    return viewers


@router.get("/my-history", response_model=List[StoryViewerPublic])
def get_my_view_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get current user's story view history
    """
    history = story_viewer_service.get_user_view_history(
        session=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return history


@router.post("/story/{story_id}/view", status_code=status.HTTP_201_CREATED)
def record_story_view(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
    view_duration: Optional[int] = Query(None, ge=0),
    device_type: Optional[str] = Query(None, max_length=50),
) -> Any:
    """
    Record that current user viewed a story
    """
    viewer = story_viewer_service.record_view(
        session=session,
        story_id=story_id,
        user_id=current_user.id,
        view_duration=view_duration,
        device_type=device_type,
    )
    return {"message": "View recorded successfully", "viewer_id": viewer.id}


@router.put("/{viewer_id}/duration", response_model=StoryViewerPublic)
def update_view_duration(
    session: SessionDep,
    current_user: CurrentUser,
    viewer_id: uuid.UUID,
    view_duration: int = Query(..., ge=0),
) -> Any:
    """
    Update view duration for a viewer record
    """
    viewer = story_viewer_service.get_viewer(session=session, viewer_id=viewer_id)
    if not viewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viewer record not found",
        )

    if viewer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this viewer record",
        )

    updated_viewer = story_viewer_service.update_view_duration(
        session=session,
        viewer_id=viewer_id,
        view_duration=view_duration,
    )
    if not updated_viewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viewer record not found",
        )
    return updated_viewer


@router.get("/story/{story_id}/analytics")
def get_story_view_analytics(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
) -> Any:
    """
    Get view analytics for a story (story owner only)
    """
    # TODO: Check if current user owns the story
    # For now, allow any authenticated user

    analytics = story_viewer_service.get_view_analytics(
        session=session, story_id=story_id
    )
    return analytics
