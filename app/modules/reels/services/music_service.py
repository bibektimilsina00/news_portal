import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.reels.crud.crud_music import crud_music
from app.modules.reels.model.music import Music
from app.modules.reels.schema.music import MusicCreate, MusicUpdate
from app.shared.deps.deps import SessionDep


class MusicService:
    """Service layer for music operations"""

    @staticmethod
    def get_music(session: SessionDep, music_id: uuid.UUID) -> Optional[Music]:
        """Get music by ID"""
        return crud_music.get(session, id=music_id)

    @staticmethod
    def get_music_list(
        session: SessionDep, skip: int = 0, limit: int = 100
    ) -> List[Music]:
        """Get list of all music"""
        return crud_music.get_multi(session, skip=skip, limit=limit)

    @staticmethod
    def create_music(session: SessionDep, music_in: MusicCreate) -> Music:
        """Create new music track"""
        return crud_music.create(session, obj_in=music_in)

    @staticmethod
    def update_music(
        session: SessionDep, music_id: uuid.UUID, music_in: MusicUpdate
    ) -> Optional[Music]:
        """Update music track"""
        music = crud_music.get(session, id=music_id)
        if not music:
            return None

        return crud_music.update(session, db_obj=music, obj_in=music_in)

    @staticmethod
    def delete_music(session: SessionDep, music_id: uuid.UUID) -> bool:
        """Delete music track"""
        music = crud_music.get(session, id=music_id)
        if not music:
            return False

        crud_music.remove(session, id=music_id)
        return True

    @staticmethod
    def get_trending_music(session: SessionDep, limit: int = 50) -> List[Music]:
        """Get trending music"""
        return crud_music.get_trending(session, limit=limit)

    @staticmethod
    def get_music_by_artist(
        session: SessionDep, artist: str, skip: int = 0, limit: int = 100
    ) -> List[Music]:
        """Get music by artist"""
        return crud_music.get_by_artist(session, artist=artist, skip=skip, limit=limit)

    @staticmethod
    def get_music_by_genre(
        session: SessionDep, genre: str, skip: int = 0, limit: int = 100
    ) -> List[Music]:
        """Get music by genre"""
        return crud_music.get_by_genre(session, genre=genre, skip=skip, limit=limit)

    @staticmethod
    def search_music(
        session: SessionDep, query: str, skip: int = 0, limit: int = 100
    ) -> List[Music]:
        """Search music by title or artist"""
        return crud_music.search_music(session, query=query, skip=skip, limit=limit)

    @staticmethod
    def increment_use_count(
        session: SessionDep, music_id: uuid.UUID
    ) -> Optional[Music]:
        """Increment music use count when used in a reel"""
        return crud_music.update_use_count(session, music_id=music_id)

    @staticmethod
    def update_trending_score(
        session: SessionDep, music_id: uuid.UUID, score: float
    ) -> Optional[Music]:
        """Update music trending score"""
        return crud_music.update_trending_score(session, music_id=music_id, score=score)


music_service = MusicService()
