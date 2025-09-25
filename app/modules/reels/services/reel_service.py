import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.modules.reels.crud.crud_reel import crud_reel
from app.modules.reels.model.reel import Reel, ReelStatus, ReelType, ReelVisibility
from app.modules.reels.schema.reel import (
    ReelCreate,
    ReelDuetCreate,
    ReelPublic,
    ReelStitchCreate,
    ReelUpdate,
)
from app.shared.deps.deps import SessionDep


class ReelService:
    """Service layer for reel operations"""

    @staticmethod
    def get_reel(session: SessionDep, reel_id: uuid.UUID) -> Optional[Reel]:
        """Get a reel by ID"""
        return crud_reel.get(session, id=reel_id)

    @staticmethod
    def get_reels_feed(
        session: SessionDep,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Reel]:
        """Get reels feed for user"""
        if user_id:
            # Personalized feed based on user's interests
            return crud_reel.get_published(session, skip=skip, limit=limit)
        else:
            # General trending feed
            return crud_reel.get_trending(session, limit=limit)

    @staticmethod
    def get_user_reels(
        session: SessionDep,
        user_id: uuid.UUID,
        include_unpublished: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Reel]:
        """Get reels by user"""
        reels = crud_reel.get_by_user(session, user_id=user_id, skip=skip, limit=limit)
        if not include_unpublished:
            reels = [reel for reel in reels if reel.status == ReelStatus.PUBLISHED]
        return reels

    @staticmethod
    def create_reel(
        session: SessionDep, reel_in: ReelCreate, user_id: uuid.UUID
    ) -> Reel:
        """Create a new reel"""
        # Create a new ReelCreate object with user_id
        reel_data = reel_in.model_dump()
        reel_data["user_id"] = user_id
        reel_data["status"] = ReelStatus.PROCESSING

        reel_create = ReelCreate(**reel_data)
        reel = crud_reel.create(session, obj_in=reel_create)
        return reel

    @staticmethod
    def update_reel(
        session: SessionDep, reel_id: uuid.UUID, reel_in: ReelUpdate, user_id: uuid.UUID
    ) -> Optional[Reel]:
        """Update a reel"""
        reel = crud_reel.get(session, id=reel_id)
        if not reel or reel.user_id != user_id:
            return None

        reel = crud_reel.update(session, db_obj=reel, obj_in=reel_in)
        return reel

    @staticmethod
    def delete_reel(
        session: SessionDep, reel_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Delete a reel"""
        reel = crud_reel.get(session, id=reel_id)
        if not reel or reel.user_id != user_id:
            return False

        crud_reel.remove(session, id=reel_id)
        return True

    @staticmethod
    def publish_reel(
        session: SessionDep, reel_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Reel]:
        """Publish a processed reel"""
        reel = crud_reel.get(session, id=reel_id)
        if not reel or reel.user_id != user_id or reel.status != ReelStatus.PROCESSING:
            return None

        return crud_reel.update_status(
            session, reel_id=reel_id, status=ReelStatus.PUBLISHED
        )

    @staticmethod
    def get_trending_reels(session: SessionDep, limit: int = 20) -> List[Reel]:
        """Get trending reels"""
        return crud_reel.get_trending(session, limit=limit)

    @staticmethod
    def search_reels_by_hashtag(
        session: SessionDep, hashtag: str, skip: int = 0, limit: int = 20
    ) -> List[Reel]:
        """Search reels by hashtag"""
        return crud_reel.get_by_hashtag(
            session, hashtag=hashtag, skip=skip, limit=limit
        )

    @staticmethod
    def get_reels_by_music(
        session: SessionDep, music_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> List[Reel]:
        """Get reels using specific music"""
        return crud_reel.get_by_music(
            session, music_id=music_id, skip=skip, limit=limit
        )

    @staticmethod
    def create_duet(
        session: SessionDep, duet_in: ReelDuetCreate, user_id: uuid.UUID
    ) -> Reel:
        """Create a duet reel"""
        original_reel = crud_reel.get(session, id=duet_in.original_reel_id)
        if not original_reel:
            raise ValueError("Original reel not found")

        reel_data = {
            "user_id": user_id,
            "type": ReelType.DUET,
            "duet_reel_id": duet_in.original_reel_id,
            "video_url": duet_in.video_url,
            "thumbnail_url": duet_in.thumbnail_url,
            "duration": duet_in.duration,
            "title": duet_in.title,
            "description": duet_in.description,
            "status": ReelStatus.PROCESSING,
        }

        reel_create = ReelCreate(**reel_data)
        reel = crud_reel.create(session, obj_in=reel_create)
        return reel

    @staticmethod
    def create_stitch(
        session: SessionDep, stitch_in: ReelStitchCreate, user_id: uuid.UUID
    ) -> Reel:
        """Create a stitch reel"""
        original_reel = crud_reel.get(session, id=stitch_in.original_reel_id)
        if not original_reel:
            raise ValueError("Original reel not found")

        reel_data = {
            "user_id": user_id,
            "type": ReelType.STITCH,
            "stitch_reel_id": stitch_in.original_reel_id,
            "video_url": stitch_in.video_url,
            "thumbnail_url": stitch_in.thumbnail_url,
            "duration": stitch_in.duration,
            "title": stitch_in.title,
            "description": stitch_in.description,
            "status": ReelStatus.PROCESSING,
        }

        reel_create = ReelCreate(**reel_data)
        reel = crud_reel.create(session, obj_in=reel_create)
        return reel

    @staticmethod
    def get_duets(
        session: SessionDep, reel_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> List[Reel]:
        """Get duets of a reel"""
        return crud_reel.get_duets(
            session, original_reel_id=reel_id, skip=skip, limit=limit
        )

    @staticmethod
    def get_stitches(
        session: SessionDep, reel_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> List[Reel]:
        """Get stitches of a reel"""
        return crud_reel.get_stitches(
            session, original_reel_id=reel_id, skip=skip, limit=limit
        )

    @staticmethod
    def update_engagement(
        session: SessionDep,
        reel_id: uuid.UUID,
        engagement_type: str,
        increment: int = 1,
    ) -> Optional[Reel]:
        """Update reel engagement metrics"""
        engagement_data = {f"{engagement_type}_count": increment}
        return crud_reel.update_engagement(
            session, reel_id=reel_id, engagement_data=engagement_data
        )


reel_service = ReelService()
