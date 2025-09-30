import uuid
from typing import Dict, List, Optional

from sqlalchemy import and_
from sqlmodel import Session, select

from app.modules.reels.model.reel import Reel, ReelStatus, ReelType
from app.modules.reels.schema.reel import ReelCreate, ReelUpdate
from app.shared.crud.base import CRUDBase


class CRUDReel(CRUDBase[Reel, ReelCreate, ReelUpdate]):
    """CRUD operations for reels"""

    def get_by_user(
        self, session: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Reel]:
        """Get reels by user"""
        statement = (
            select(Reel)
            .where(Reel.user_id == user_id)
            .order_by(Reel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()

    def get_published(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Reel]:
        """Get published reels"""
        statement = (
            select(Reel)
            .where(Reel.status == ReelStatus.PUBLISHED)
            .order_by(Reel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()

    def get_trending(self, session: Session, *, limit: int = 20) -> List[Reel]:
        """Get trending reels based on engagement"""
        statement = (
            select(Reel)
            .where(Reel.status == ReelStatus.PUBLISHED)
            .order_by(
                (Reel.like_count + Reel.comment_count * 2 + Reel.share_count * 3).desc()
            )
            .limit(limit)
        )
        return session.exec(statement).all()

    def get_by_hashtag(
        self, session: Session, *, hashtag: str, skip: int = 0, limit: int = 100
    ) -> List[Reel]:
        """Get reels by hashtag"""
        statement = (
            select(Reel)
            .where(
                and_(
                    Reel.status == ReelStatus.PUBLISHED,
                    Reel.hashtags.contains([hashtag]),
                )
            )
            .order_by(Reel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()

    def get_by_music(
        self, session: Session, *, music_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Reel]:
        """Get reels by music"""
        statement = (
            select(Reel)
            .where(and_(Reel.status == ReelStatus.PUBLISHED, Reel.music_id == music_id))
            .order_by(Reel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()

    def get_duets(
        self,
        session: Session,
        *,
        original_reel_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Reel]:
        """Get duets of a reel"""
        statement = (
            select(Reel)
            .where(
                and_(
                    Reel.type == ReelType.DUET,
                    Reel.duet_reel_id == original_reel_id,
                    Reel.status == ReelStatus.PUBLISHED,
                )
            )
            .order_by(Reel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()

    def get_stitches(
        self,
        session: Session,
        *,
        original_reel_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Reel]:
        """Get stitches of a reel"""
        statement = (
            select(Reel)
            .where(
                and_(
                    Reel.type == ReelType.STITCH,
                    Reel.stitch_reel_id == original_reel_id,
                    Reel.status == ReelStatus.PUBLISHED,
                )
            )
            .order_by(Reel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()

    def update_engagement(
        self, session: Session, *, reel_id: uuid.UUID, engagement_data: Dict[str, int]
    ) -> Optional[Reel]:
        """Update reel engagement metrics"""
        reel = self.get(session, id=reel_id)
        if not reel:
            return None

        for field, value in engagement_data.items():
            if hasattr(reel, field):
                setattr(reel, field, getattr(reel, field) + value)

        session.commit()
        session.refresh(reel)
        return reel

    def update_status(
        self, session: Session, *, reel_id: uuid.UUID, status: ReelStatus
    ) -> Optional[Reel]:
        """Update reel processing status"""
        reel = self.get(session, id=reel_id)
        if not reel:
            return None

        reel.status = status
        if status == ReelStatus.PUBLISHED:
            from datetime import datetime

            reel.published_at = datetime.utcnow()

        session.commit()
        session.refresh(reel)
        return reel


crud_reel = CRUDReel(Reel)
