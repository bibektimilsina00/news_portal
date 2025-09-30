import uuid
from typing import List, Optional


from app.modules.stories.crud.crud_story import crud_story
from app.modules.stories.model.story import Story
from app.modules.stories.schema.story import StoryCreate, StoryUpdate
from app.shared.deps.deps import SessionDep


class StoryService:
    """Service layer for story operations"""

    @staticmethod
    def get_story(session: SessionDep, story_id: uuid.UUID) -> Optional[Story]:
        """Get a story by ID"""
        return crud_story.get(session, id=story_id)

    @staticmethod
    def get_active_stories(
        session: SessionDep,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Story]:
        """Get active stories"""
        return crud_story.get_active_stories(session, skip=skip, limit=limit)

    @staticmethod
    def get_user_stories(
        session: SessionDep,
        user_id: uuid.UUID,
        include_expired: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Story]:
        """Get stories for a specific user"""
        return crud_story.get_user_stories(
            session,
            user_id=user_id,
            include_expired=include_expired,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def create_story(
        session: SessionDep, story_in: StoryCreate, user_id: uuid.UUID
    ) -> Story:
        """Create a new story"""
        return crud_story.create_with_expiration(
            session, obj_in=story_in, user_id=user_id
        )

    @staticmethod
    def update_story(
        session: SessionDep, story_id: uuid.UUID, story_in: StoryUpdate
    ) -> Optional[Story]:
        """Update an existing story"""
        story = crud_story.get(session, id=story_id)
        if not story:
            return None
        return crud_story.update(session, db_obj=story, obj_in=story_in)

    @staticmethod
    def delete_story(session: SessionDep, story_id: uuid.UUID) -> bool:
        """Delete a story"""
        story = crud_story.get(session, id=story_id)
        if story:
            crud_story.remove(session, id=story_id)
            return True
        return False


story_service = StoryService()
