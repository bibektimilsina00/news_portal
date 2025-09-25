import uuid
from typing import List, Optional

from app.modules.stories.crud.crud_highlight import crud_highlight
from app.modules.stories.model.highlight import StoryHighlight
from app.modules.stories.schema.highlight import (
    StoryHighlightCreate,
    StoryHighlightPublic,
    StoryHighlightUpdate,
)
from app.shared.deps.deps import SessionDep


class StoryHighlightService:
    """Service layer for story highlight operations"""

    @staticmethod
    def get_highlight(
        session: SessionDep, highlight_id: uuid.UUID
    ) -> Optional[StoryHighlight]:
        """Get a highlight by ID"""
        return crud_highlight.get(session, id=highlight_id)

    @staticmethod
    def get_user_highlights(
        session: SessionDep,
        user_id: uuid.UUID,
        include_archived: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryHighlight]:
        """Get highlights for a specific user"""
        return crud_highlight.get_user_highlights(
            session,
            user_id=user_id,
            include_archived=include_archived,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def create_highlight(
        session: SessionDep,
        highlight_in: StoryHighlightCreate,
        user_id: uuid.UUID,
    ) -> StoryHighlight:
        """Create a new highlight"""
        # Add user_id to the highlight data
        highlight_data = highlight_in.model_dump()
        highlight_data["user_id"] = user_id

        # Create highlight
        highlight = crud_highlight.create(
            session, obj_in=StoryHighlightCreate(**highlight_data)
        )

        # TODO: Add stories to highlight if story_ids provided
        # if highlight_in.story_ids:
        #     crud_highlight.add_stories_to_highlight(
        #         session, highlight_id=highlight.id, story_ids=highlight_in.story_ids
        #     )

        return highlight

    @staticmethod
    def update_highlight(
        session: SessionDep,
        highlight_id: uuid.UUID,
        highlight_in: StoryHighlightUpdate,
    ) -> Optional[StoryHighlight]:
        """Update an existing highlight"""
        highlight = crud_highlight.get(session, id=highlight_id)
        if not highlight:
            return None

        # TODO: Update stories if story_ids provided
        # if highlight_in.story_ids:
        #     # Remove existing stories and add new ones
        #     pass

        return crud_highlight.update(session, db_obj=highlight, obj_in=highlight_in)

    @staticmethod
    def delete_highlight(session: SessionDep, highlight_id: uuid.UUID) -> bool:
        """Delete a highlight"""
        highlight = crud_highlight.get(session, id=highlight_id)
        if highlight:
            crud_highlight.remove(session, id=highlight_id)
            return True
        return False

    @staticmethod
    def archive_highlight(
        session: SessionDep, highlight_id: uuid.UUID
    ) -> Optional[StoryHighlight]:
        """Archive a highlight"""
        highlight = crud_highlight.get(session, id=highlight_id)
        if highlight:
            update_data = StoryHighlightUpdate(is_archived=True)
            return crud_highlight.update(session, db_obj=highlight, obj_in=update_data)
        return None

    @staticmethod
    def unarchive_highlight(
        session: SessionDep, highlight_id: uuid.UUID
    ) -> Optional[StoryHighlight]:
        """Unarchive a highlight"""
        highlight = crud_highlight.get(session, id=highlight_id)
        if highlight:
            update_data = StoryHighlightUpdate(is_archived=False)
            return crud_highlight.update(session, db_obj=highlight, obj_in=update_data)
        return None


story_highlight_service = StoryHighlightService()
