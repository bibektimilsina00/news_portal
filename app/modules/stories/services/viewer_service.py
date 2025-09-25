import uuid
from typing import Any, Dict, List, Optional

from app.modules.stories.crud.crud_viewer import crud_viewer
from app.modules.stories.model.viewer import StoryViewer
from app.modules.stories.schema.viewer import (
    StoryViewerCreate,
    StoryViewerPublic,
    StoryViewerUpdate,
)
from app.shared.deps.deps import SessionDep


class StoryViewerService:
    """Service layer for story viewer operations"""

    @staticmethod
    def get_viewer(session: SessionDep, viewer_id: uuid.UUID) -> Optional[StoryViewer]:
        """Get a viewer record by ID"""
        return crud_viewer.get(session, id=viewer_id)

    @staticmethod
    def get_story_viewers(
        session: SessionDep,
        story_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryViewer]:
        """Get viewers for a specific story"""
        return crud_viewer.get_story_viewers(
            session, story_id=story_id, skip=skip, limit=limit
        )

    @staticmethod
    def get_user_view_history(
        session: SessionDep,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryViewer]:
        """Get view history for a specific user"""
        return crud_viewer.get_user_view_history(
            session, user_id=user_id, skip=skip, limit=limit
        )

    @staticmethod
    def record_view(
        session: SessionDep,
        story_id: uuid.UUID,
        user_id: uuid.UUID,
        view_duration: Optional[int] = None,
        device_type: Optional[str] = None,
    ) -> StoryViewer:
        """Record a story view"""
        return crud_viewer.record_view(
            session,
            story_id=story_id,
            user_id=user_id,
            view_duration=view_duration,
            device_type=device_type,
        )

    @staticmethod
    def update_view_duration(
        session: SessionDep,
        viewer_id: uuid.UUID,
        view_duration: int,
    ) -> Optional[StoryViewer]:
        """Update view duration for a viewer record"""
        viewer = crud_viewer.get(session, id=viewer_id)
        if viewer:
            update_data = StoryViewerUpdate(view_duration=view_duration)
            return crud_viewer.update(session, db_obj=viewer, obj_in=update_data)
        return None

    @staticmethod
    def get_view_analytics(session: SessionDep, story_id: uuid.UUID) -> Dict[str, Any]:
        """Get view analytics for a story"""
        return crud_viewer.get_view_analytics(session, story_id=story_id)


story_viewer_service = StoryViewerService()
