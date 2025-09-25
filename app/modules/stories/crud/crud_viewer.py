import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlmodel import Session, select

from app.modules.stories.model.viewer import StoryViewer
from app.modules.stories.schema.viewer import StoryViewerCreate, StoryViewerUpdate
from app.shared.crud.base import CRUDBase


class CRUDStoryViewer(CRUDBase[StoryViewer, StoryViewerCreate, StoryViewerUpdate]):
    """CRUD operations for story viewers"""

    def get_story_viewers(
        self,
        session: Session,
        *,
        story_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryViewer]:
        """Get viewers for a specific story"""
        statement = select(StoryViewer).where(StoryViewer.story_id == story_id)
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_user_view_history(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryViewer]:
        """Get view history for a specific user"""
        statement = select(StoryViewer).where(StoryViewer.user_id == user_id)
        return list(session.exec(statement.offset(skip).limit(limit)))

    def record_view(
        self,
        session: Session,
        *,
        story_id: uuid.UUID,
        user_id: uuid.UUID,
        view_duration: Optional[int] = None,
        device_type: Optional[str] = None,
    ) -> StoryViewer:
        """Record a story view"""
        # Check if user already viewed this story
        existing_view = session.exec(
            select(StoryViewer)
            .where(StoryViewer.story_id == story_id)
            .where(StoryViewer.user_id == user_id)
            .limit(1)
        ).first()

        if existing_view:
            # Update existing view
            if view_duration is not None:
                existing_view.view_duration = view_duration
            if device_type is not None:
                existing_view.device_type = device_type
            session.commit()
            session.refresh(existing_view)
            return existing_view
        else:
            # Create new view record
            viewer_in = StoryViewerCreate(
                story_id=story_id,
                view_duration=view_duration,
                device_type=device_type,
            )
            return self.create(session, obj_in=viewer_in)

    def get_view_analytics(
        self,
        session: Session,
        *,
        story_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Get view analytics for a story"""
        # Count total views
        total_views_result = session.exec(
            select(func.count())
            .select_from(StoryViewer)
            .where(StoryViewer.story_id == story_id)
        ).first()

        # Count unique viewers
        unique_viewers_result = session.exec(
            select(func.count(func.distinct(StoryViewer.user_id))).where(
                StoryViewer.story_id == story_id
            )
        ).first()

        return {
            "total_views": total_views_result or 0,
            "unique_viewers": unique_viewers_result or 0,
            "average_view_duration": 0.0,  # Simplified for now
        }


crud_viewer = CRUDStoryViewer(StoryViewer)
