import uuid
from typing import List, Optional

from sqlalchemy import and_, func, or_
from sqlmodel import Session, select

from app.modules.reels.model.music import Music
from app.modules.reels.schema.music import MusicCreate, MusicUpdate
from app.shared.crud.base import CRUDBase


class CRUDMusic(CRUDBase[Music, MusicCreate, MusicUpdate]):
    """CRUD operations for music tracks"""

    def get_by_artist(
        self, session: Session, *, artist: str, skip: int = 0, limit: int = 100
    ) -> List[Music]:
        """Get music by artist"""
        statement = (
            select(Music)
            .where(Music.artist == artist)
            .order_by(Music.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_by_genre(
        self, session: Session, *, genre: str, skip: int = 0, limit: int = 100
    ) -> List[Music]:
        """Get music by genre"""
        statement = (
            select(Music)
            .where(Music.genre == genre)
            .order_by(Music.use_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_trending(self, session: Session, *, limit: int = 50) -> List[Music]:
        """Get trending music"""
        statement = select(Music).order_by(Music.trending_score.desc()).limit(limit)
        return list(session.exec(statement))

    def search_music(
        self, session: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Music]:
        """Search music by title or artist"""
        search_term = f"%{query}%"
        statement = (
            select(Music)
            .where(or_(Music.title.ilike(search_term), Music.artist.ilike(search_term)))
            .order_by(Music.use_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def update_use_count(
        self, session: Session, *, music_id: uuid.UUID
    ) -> Optional[Music]:
        """Increment music use count"""
        music = self.get(session, id=music_id)
        if not music:
            return None

        music.use_count += 1
        session.commit()
        session.refresh(music)
        return music

    def update_trending_score(
        self, session: Session, *, music_id: uuid.UUID, score: float
    ) -> Optional[Music]:
        """Update music trending score"""
        music = self.get(session, id=music_id)
        if not music:
            return None

        music.trending_score = score
        session.commit()
        session.refresh(music)
        return music


crud_music = CRUDMusic(Music)
