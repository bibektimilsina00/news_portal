import uuid
from typing import Any, List

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.reels.schema.music import MusicCreate, MusicPublic, MusicUpdate
from app.modules.reels.services.music_service import music_service
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter(prefix="/music", tags=["reel-music"])


@router.get("/", response_model=List[MusicPublic])
def get_music_list(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
) -> Any:
    """
    Get list of all music tracks
    """
    music = music_service.get_music_list(session=session, skip=skip, limit=limit)
    return music


@router.get("/trending", response_model=List[MusicPublic])
def get_trending_music(
    session: SessionDep,
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get trending music tracks
    """
    music = music_service.get_trending_music(session=session, limit=limit)
    return music


@router.get("/search", response_model=List[MusicPublic])
def search_music(
    session: SessionDep,
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Search music by title or artist
    """
    music = music_service.search_music(session=session, query=q, skip=skip, limit=limit)
    return music


@router.get("/artist/{artist}", response_model=List[MusicPublic])
def get_music_by_artist(
    session: SessionDep,
    artist: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get music by artist
    """
    music = music_service.get_music_by_artist(
        session=session, artist=artist, skip=skip, limit=limit
    )
    return music


@router.get("/genre/{genre}", response_model=List[MusicPublic])
def get_music_by_genre(
    session: SessionDep,
    genre: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get music by genre
    """
    music = music_service.get_music_by_genre(
        session=session, genre=genre, skip=skip, limit=limit
    )
    return music


@router.post("/", response_model=MusicPublic)
def create_music(
    session: SessionDep,
    current_user: CurrentUser,
    music_in: MusicCreate,
) -> Any:
    """
    Create a new music track (admin only)
    """
    # TODO: Add admin check
    music = music_service.create_music(session=session, music_in=music_in)
    return music


@router.get("/{music_id}", response_model=MusicPublic)
def get_music(
    session: SessionDep,
    music_id: uuid.UUID,
) -> Any:
    """
    Get a specific music track
    """
    music = music_service.get_music(session=session, music_id=music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found",
        )
    return music


@router.put("/{music_id}", response_model=MusicPublic)
def update_music(
    session: SessionDep,
    current_user: CurrentUser,
    music_id: uuid.UUID,
    music_in: MusicUpdate,
) -> Any:
    """
    Update a music track (admin only)
    """
    # TODO: Add admin check
    music = music_service.update_music(
        session=session, music_id=music_id, music_in=music_in
    )
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found",
        )
    return music


@router.delete("/{music_id}", response_model=Message)
def delete_music(
    session: SessionDep,
    current_user: CurrentUser,
    music_id: uuid.UUID,
) -> Any:
    """
    Delete a music track (admin only)
    """
    # TODO: Add admin check
    success = music_service.delete_music(session=session, music_id=music_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found",
        )
    return Message(message="Music deleted successfully")


@router.post("/{music_id}/use", response_model=Message)
def use_music(
    session: SessionDep,
    current_user: CurrentUser,
    music_id: uuid.UUID,
) -> Any:
    """
    Record music usage (called when music is used in a reel)
    """
    music = music_service.increment_use_count(session=session, music_id=music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found",
        )
    return Message(message="Music usage recorded successfully")
