import uuid
from typing import Dict, List, Optional

from sqlmodel import Session, select

from app.modules.stories.model.interaction import InteractionType, StoryInteraction
from app.modules.stories.schema.interaction import (
    StoryInteractionCreate,
    StoryInteractionUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDStoryInteraction(
    CRUDBase[StoryInteraction, StoryInteractionCreate, StoryInteractionUpdate]
):
    """CRUD operations for story interactions"""

    def get_story_interactions(
        self,
        session: Session,
        *,
        story_id: uuid.UUID,
        interaction_type: Optional[InteractionType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryInteraction]:
        """Get interactions for a specific story"""
        statement = select(StoryInteraction).where(
            StoryInteraction.story_id == story_id
        )

        if interaction_type:
            statement = statement.where(
                StoryInteraction.interaction_type == interaction_type
            )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_user_interactions(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        story_id: Optional[uuid.UUID] = None,
        interaction_type: Optional[InteractionType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryInteraction]:
        """Get interactions by a specific user"""
        statement = select(StoryInteraction).where(StoryInteraction.user_id == user_id)

        if story_id:
            statement = statement.where(StoryInteraction.story_id == story_id)

        if interaction_type:
            statement = statement.where(
                StoryInteraction.interaction_type == interaction_type
            )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_poll_results(
        self,
        session: Session,
        *,
        story_id: uuid.UUID,
    ) -> Dict[str, int]:
        """Get poll voting results for a story"""
        statement = (
            select(StoryInteraction.option_selected)
            .where(StoryInteraction.story_id == story_id)
            .where(StoryInteraction.interaction_type == InteractionType.POLL_VOTE)
        )

        results = {}
        rows = list(session.exec(statement))
        for row in rows:
            option = row
            if option:
                results[option] = results.get(option, 0) + 1

        return results

    def has_user_interacted(
        self,
        session: Session,
        *,
        story_id: uuid.UUID,
        user_id: uuid.UUID,
        interaction_type: Optional[InteractionType] = None,
    ) -> bool:
        """Check if user has already interacted with a story"""
        statement = (
            select(StoryInteraction)
            .where(StoryInteraction.story_id == story_id)
            .where(StoryInteraction.user_id == user_id)
        )

        if interaction_type:
            statement = statement.where(
                StoryInteraction.interaction_type == interaction_type
            )

        result = session.exec(statement.limit(1)).first()
        return result is not None


crud_interaction = CRUDStoryInteraction(StoryInteraction)
