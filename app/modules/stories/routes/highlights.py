import uuid
from typing import Any, List

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.stories.schema.highlight import (
    StoryHighlightCreate,
    StoryHighlightPublic,
    StoryHighlightUpdate,
)
from app.modules.stories.services.highlight_service import story_highlight_service
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter(prefix="/highlights", tags=["story-highlights"])


@router.get("/", response_model=List[StoryHighlightPublic])
def get_user_highlights(
    session: SessionDep,
    current_user: CurrentUser,
    include_archived: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get current user's story highlights
    """
    highlights = story_highlight_service.get_user_highlights(
        session=session,
        user_id=current_user.id,
        include_archived=include_archived,
        skip=skip,
        limit=limit,
    )
    return highlights


@router.post(
    "/", response_model=StoryHighlightPublic, status_code=status.HTTP_201_CREATED
)
def create_highlight(
    session: SessionDep,
    current_user: CurrentUser,
    highlight_in: StoryHighlightCreate,
) -> Any:
    """
    Create a new story highlight
    """
    highlight = story_highlight_service.create_highlight(
        session=session,
        highlight_in=highlight_in,
        user_id=current_user.id,
    )
    return highlight


@router.get("/{highlight_id}", response_model=StoryHighlightPublic)
def get_highlight(
    session: SessionDep,
    current_user: CurrentUser,
    highlight_id: uuid.UUID,
) -> Any:
    """
    Get a specific highlight by ID
    """
    highlight = story_highlight_service.get_highlight(
        session=session, highlight_id=highlight_id
    )
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )

    if highlight.user_id != current_user.id and highlight.is_private:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this highlight",
        )

    return highlight


@router.put("/{highlight_id}", response_model=StoryHighlightPublic)
def update_highlight(
    session: SessionDep,
    current_user: CurrentUser,
    highlight_id: uuid.UUID,
    highlight_in: StoryHighlightUpdate,
) -> Any:
    """
    Update a highlight
    """
    highlight = story_highlight_service.get_highlight(
        session=session, highlight_id=highlight_id
    )
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )

    if highlight.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this highlight",
        )

    updated_highlight = story_highlight_service.update_highlight(
        session=session,
        highlight_id=highlight_id,
        highlight_in=highlight_in,
    )
    if not updated_highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )
    return updated_highlight


@router.delete("/{highlight_id}", response_model=Message)
def delete_highlight(
    session: SessionDep,
    current_user: CurrentUser,
    highlight_id: uuid.UUID,
) -> Any:
    """
    Delete a highlight
    """
    highlight = story_highlight_service.get_highlight(
        session=session, highlight_id=highlight_id
    )
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )

    if highlight.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this highlight",
        )

    deleted = story_highlight_service.delete_highlight(
        session=session, highlight_id=highlight_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )

    return Message(message="Highlight deleted successfully")


@router.post("/{highlight_id}/archive", response_model=StoryHighlightPublic)
def archive_highlight(
    session: SessionDep,
    current_user: CurrentUser,
    highlight_id: uuid.UUID,
) -> Any:
    """
    Archive a highlight
    """
    highlight = story_highlight_service.get_highlight(
        session=session, highlight_id=highlight_id
    )
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )

    if highlight.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive this highlight",
        )

    archived_highlight = story_highlight_service.archive_highlight(
        session=session, highlight_id=highlight_id
    )
    if not archived_highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )
    return archived_highlight


@router.post("/{highlight_id}/unarchive", response_model=StoryHighlightPublic)
def unarchive_highlight(
    session: SessionDep,
    current_user: CurrentUser,
    highlight_id: uuid.UUID,
) -> Any:
    """
    Unarchive a highlight
    """
    highlight = story_highlight_service.get_highlight(
        session=session, highlight_id=highlight_id
    )
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )

    if highlight.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to unarchive this highlight",
        )

    unarchived_highlight = story_highlight_service.unarchive_highlight(
        session=session, highlight_id=highlight_id
    )
    if not unarchived_highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found",
        )
    return unarchived_highlight
