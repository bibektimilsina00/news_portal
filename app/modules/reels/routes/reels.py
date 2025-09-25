import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.modules.reels.schema.reel import (
    ReelCreate,
    ReelDuetCreate,
    ReelList,
    ReelPublic,
    ReelStitchCreate,
    ReelUpdate,
)
from app.modules.reels.services.reel_service import reel_service
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter(prefix="/reels", tags=["reels"])


@router.get("/", response_model=List[ReelPublic])
def get_reels_feed(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get reels feed
    """
    reels = reel_service.get_reels_feed(
        session=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return reels


@router.get("/trending", response_model=List[ReelPublic])
def get_trending_reels(
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get trending reels
    """
    reels = reel_service.get_trending_reels(session=session, limit=limit)
    return reels


@router.get("/hashtag/{hashtag}", response_model=List[ReelPublic])
def get_reels_by_hashtag(
    session: SessionDep,
    hashtag: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get reels by hashtag
    """
    reels = reel_service.search_reels_by_hashtag(
        session=session, hashtag=hashtag, skip=skip, limit=limit
    )
    return reels


@router.get("/music/{music_id}", response_model=List[ReelPublic])
def get_reels_by_music(
    session: SessionDep,
    music_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get reels using specific music
    """
    reels = reel_service.get_reels_by_music(
        session=session, music_id=music_id, skip=skip, limit=limit
    )
    return reels


@router.get("/my-reels", response_model=List[ReelPublic])
def get_my_reels(
    session: SessionDep,
    current_user: CurrentUser,
    include_unpublished: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get current user's reels
    """
    reels = reel_service.get_user_reels(
        session=session,
        user_id=current_user.id,
        include_unpublished=include_unpublished,
        skip=skip,
        limit=limit,
    )
    return reels


@router.post("/", response_model=ReelPublic)
def create_reel(
    session: SessionDep,
    current_user: CurrentUser,
    reel_in: ReelCreate,
) -> Any:
    """
    Create a new reel
    """
    reel = reel_service.create_reel(
        session=session, reel_in=reel_in, user_id=current_user.id
    )
    return reel


@router.get("/{reel_id}", response_model=ReelPublic)
def get_reel(
    session: SessionDep,
    current_user: CurrentUser,
    reel_id: uuid.UUID,
) -> Any:
    """
    Get a specific reel
    """
    reel = reel_service.get_reel(session=session, reel_id=reel_id)
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found",
        )
    return reel


@router.put("/{reel_id}", response_model=ReelPublic)
def update_reel(
    session: SessionDep,
    current_user: CurrentUser,
    reel_id: uuid.UUID,
    reel_in: ReelUpdate,
) -> Any:
    """
    Update a reel
    """
    reel = reel_service.update_reel(
        session=session, reel_id=reel_id, reel_in=reel_in, user_id=current_user.id
    )
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found or not authorized",
        )
    return reel


@router.delete("/{reel_id}", response_model=Message)
def delete_reel(
    session: SessionDep,
    current_user: CurrentUser,
    reel_id: uuid.UUID,
) -> Any:
    """
    Delete a reel
    """
    success = reel_service.delete_reel(
        session=session, reel_id=reel_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found or not authorized",
        )
    return Message(message="Reel deleted successfully")


@router.post("/{reel_id}/publish", response_model=ReelPublic)
def publish_reel(
    session: SessionDep,
    current_user: CurrentUser,
    reel_id: uuid.UUID,
) -> Any:
    """
    Publish a processed reel
    """
    reel = reel_service.publish_reel(
        session=session, reel_id=reel_id, user_id=current_user.id
    )
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found or not authorized",
        )
    return reel


@router.post("/duet", response_model=ReelPublic)
def create_duet(
    session: SessionDep,
    current_user: CurrentUser,
    duet_in: ReelDuetCreate,
) -> Any:
    """
    Create a duet reel
    """
    try:
        reel = reel_service.create_duet(
            session=session, duet_in=duet_in, user_id=current_user.id
        )
        return reel
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/stitch", response_model=ReelPublic)
def create_stitch(
    session: SessionDep,
    current_user: CurrentUser,
    stitch_in: ReelStitchCreate,
) -> Any:
    """
    Create a stitch reel
    """
    try:
        reel = reel_service.create_stitch(
            session=session, stitch_in=stitch_in, user_id=current_user.id
        )
        return reel
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{reel_id}/duets", response_model=List[ReelPublic])
def get_duets(
    session: SessionDep,
    reel_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get duets of a reel
    """
    duets = reel_service.get_duets(
        session=session, reel_id=reel_id, skip=skip, limit=limit
    )
    return duets


@router.get("/{reel_id}/stitches", response_model=List[ReelPublic])
def get_stitches(
    session: SessionDep,
    reel_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get stitches of a reel
    """
    stitches = reel_service.get_stitches(
        session=session, reel_id=reel_id, skip=skip, limit=limit
    )
    return stitches


@router.post("/{reel_id}/like", response_model=Message)
def like_reel(
    session: SessionDep,
    current_user: CurrentUser,
    reel_id: uuid.UUID,
) -> Any:
    """
    Like a reel
    """
    reel = reel_service.update_engagement(
        session=session, reel_id=reel_id, engagement_type="like"
    )
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found",
        )
    return Message(message="Reel liked successfully")


@router.post("/{reel_id}/view", response_model=Message)
def view_reel(
    session: SessionDep,
    current_user: CurrentUser,
    reel_id: uuid.UUID,
) -> Any:
    """
    Record a view on a reel
    """
    reel = reel_service.update_engagement(
        session=session, reel_id=reel_id, engagement_type="view"
    )
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found",
        )
    return Message(message="View recorded successfully")
