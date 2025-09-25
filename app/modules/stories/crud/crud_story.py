import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func
from sqlmodel import Session, select

from app.modules.stories.model.story import Story, StoryStatus, StoryVisibility
from app.modules.stories.schema.story import StoryCreate, StoryUpdate
from app.shared.crud.base import CRUDBase


class CRUDStory(CRUDBase[Story, StoryCreate, StoryUpdate]):
    """CRUD operations for stories"""

    def get_active_stories(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Story]:
        """Get active (non-expired) stories"""
        now = datetime.utcnow()
        statement = (
            select(Story)
            .where(and_(Story.status == StoryStatus.ACTIVE, Story.expires_at > now))
            .order_by(Story.created_at.desc())
        )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_user_stories(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        include_expired: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Story]:
        """Get stories for a specific user"""
        statement = select(Story).where(Story.user_id == user_id)

        if not include_expired:
            now = datetime.utcnow()
            statement = statement.where(Story.expires_at > now)

        statement = statement.order_by(Story.created_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def create_with_expiration(
        self,
        session: Session,
        *,
        obj_in: StoryCreate,
        user_id: uuid.UUID,
    ) -> Story:
        """Create a story with automatic expiration in 24 hours"""
        db_obj = Story.from_orm(obj_in)
        db_obj.user_id = user_id
        db_obj.expires_at = datetime.utcnow() + timedelta(hours=24)

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


crud_story = CRUDStory(Story)
