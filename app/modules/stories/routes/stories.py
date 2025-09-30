import uuid
from typing import Any, List

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.stories.schema.story import StoryCreate, StoryPublic, StoryUpdate
from app.modules.stories.services.story_service import story_service
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/", response_model=List[StoryPublic])
def get_stories(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get active stories feed
    """
    stories = story_service.get_active_stories(
        session=session,
        skip=skip,
        limit=limit,
    )
    return stories


@router.get("/my-stories", response_model=List[StoryPublic])
def get_my_stories(
    session: SessionDep,
    current_user: CurrentUser,
    include_expired: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get current user's stories
    """
    stories = story_service.get_user_stories(
        session=session,
        user_id=current_user.id,
        include_expired=include_expired,
        skip=skip,
        limit=limit,
    )
    return stories


@router.post("/", response_model=StoryPublic, status_code=status.HTTP_201_CREATED)
def create_story(
    session: SessionDep,
    current_user: CurrentUser,
    story_in: StoryCreate,
) -> Any:
    """
    Create a new story
    """
    story = story_service.create_story(
        session=session,
        story_in=story_in,
        user_id=current_user.id,
    )
    return story


@router.get("/{story_id}", response_model=StoryPublic)
def get_story(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
) -> Any:
    """
    Get a specific story by ID
    """
    story = story_service.get_story(session=session, story_id=story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )
    return story


@router.put("/{story_id}", response_model=StoryPublic)
def update_story(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
    story_in: StoryUpdate,
) -> Any:
    """
    Update a story
    """
    story = story_service.get_story(session=session, story_id=story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )

    if story.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this story",
        )

    updated_story = story_service.update_story(
        session=session,
        story_id=story_id,
        story_in=story_in,
    )
    if not updated_story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )
    return updated_story


@router.delete("/{story_id}", response_model=Message)
def delete_story(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
) -> Any:
    """
    Delete a story
    """
    story = story_service.get_story(session=session, story_id=story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )

    if story.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this story",
        )

    deleted = story_service.delete_story(session=session, story_id=story_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )

    return Message(message="Story deleted successfully")
