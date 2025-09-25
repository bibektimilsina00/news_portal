import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc
from sqlmodel import Session, select

from app.modules.stories.model.highlight import StoryHighlight
from app.modules.stories.schema.highlight import (
    StoryHighlightCreate,
    StoryHighlightUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDStoryHighlight(
    CRUDBase[StoryHighlight, StoryHighlightCreate, StoryHighlightUpdate]
):
    """CRUD operations for story highlights"""

    def get_user_highlights(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        include_archived: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryHighlight]:
        """Get highlights for a specific user"""
        statement = select(StoryHighlight).where(StoryHighlight.user_id == user_id)

        if not include_archived:
            statement = statement.where(StoryHighlight.is_archived == False)

        # statement = statement.order_by(StoryHighlight.created_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_highlight_with_stories(
        self,
        session: Session,
        *,
        highlight_id: uuid.UUID,
    ) -> Optional[StoryHighlight]:
        """Get a highlight with its associated stories"""
        statement = select(StoryHighlight).where(StoryHighlight.id == highlight_id)
        return session.exec(statement).first()

    def add_stories_to_highlight(
        self,
        session: Session,
        *,
        highlight_id: uuid.UUID,
        story_ids: List[uuid.UUID],
    ) -> bool:
        """Add stories to a highlight"""
        # This would require a many-to-many relationship table
        # For now, we'll implement this when the relationship is properly set up
        # TODO: Implement when story-highlight relationship is complete
        return True

    def remove_stories_from_highlight(
        self,
        session: Session,
        *,
        highlight_id: uuid.UUID,
        story_ids: List[uuid.UUID],
    ) -> bool:
        """Remove stories from a highlight"""
        # TODO: Implement when story-highlight relationship is complete
        return True


crud_highlight = CRUDStoryHighlight(StoryHighlight)
