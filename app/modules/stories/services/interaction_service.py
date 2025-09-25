import uuid
from typing import Dict, List, Optional

from app.modules.stories.crud.crud_interaction import crud_interaction
from app.modules.stories.model.interaction import InteractionType, StoryInteraction
from app.modules.stories.schema.interaction import (
    StoryInteractionCreate,
    StoryInteractionPublic,
    StoryInteractionUpdate,
)
from app.shared.deps.deps import SessionDep


class StoryInteractionService:
    """Service layer for story interaction operations"""

    @staticmethod
    def get_interaction(
        session: SessionDep, interaction_id: uuid.UUID
    ) -> Optional[StoryInteraction]:
        """Get an interaction by ID"""
        return crud_interaction.get(session, id=interaction_id)

    @staticmethod
    def get_story_interactions(
        session: SessionDep,
        story_id: uuid.UUID,
        interaction_type: Optional[InteractionType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryInteraction]:
        """Get interactions for a specific story"""
        return crud_interaction.get_story_interactions(
            session,
            story_id=story_id,
            interaction_type=interaction_type,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def create_interaction(
        session: SessionDep,
        interaction_in: StoryInteractionCreate,
        user_id: uuid.UUID,
    ) -> StoryInteraction:
        """Create a new interaction"""
        # Add user_id to the interaction data
        interaction_data = interaction_in.model_dump()
        interaction_data["user_id"] = user_id

        interaction = crud_interaction.create(
            session, obj_in=StoryInteractionCreate(**interaction_data)
        )
        return interaction

    @staticmethod
    def update_interaction(
        session: SessionDep,
        interaction_id: uuid.UUID,
        interaction_in: StoryInteractionUpdate,
    ) -> Optional[StoryInteraction]:
        """Update an existing interaction"""
        interaction = crud_interaction.get(session, id=interaction_id)
        if not interaction:
            return None
        return crud_interaction.update(
            session, db_obj=interaction, obj_in=interaction_in
        )

    @staticmethod
    def delete_interaction(session: SessionDep, interaction_id: uuid.UUID) -> bool:
        """Delete an interaction"""
        interaction = crud_interaction.get(session, id=interaction_id)
        if interaction:
            crud_interaction.remove(session, id=interaction_id)
            return True
        return False

    @staticmethod
    def vote_poll(
        session: SessionDep,
        story_id: uuid.UUID,
        user_id: uuid.UUID,
        option_selected: str,
    ) -> StoryInteraction:
        """Vote in a poll"""
        # Check if user already voted
        if crud_interaction.has_user_interacted(
            session,
            story_id=story_id,
            user_id=user_id,
            interaction_type=InteractionType.POLL_VOTE,
        ):
            # Update existing vote
            existing_interactions = crud_interaction.get_user_interactions(
                session,
                user_id=user_id,
                story_id=story_id,
                interaction_type=InteractionType.POLL_VOTE,
            )
            if existing_interactions:
                interaction = existing_interactions[0]
                update_data = StoryInteractionUpdate(option_selected=option_selected)
                return crud_interaction.update(
                    session, db_obj=interaction, obj_in=update_data
                )

        # Create new vote
        interaction_in = StoryInteractionCreate(
            story_id=story_id,
            interaction_type=InteractionType.POLL_VOTE,
            option_selected=option_selected,
        )
        return crud_interaction.create(session, obj_in=interaction_in)

    @staticmethod
    def submit_question_reply(
        session: SessionDep,
        story_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> StoryInteraction:
        """Submit a reply to a question"""
        interaction_in = StoryInteractionCreate(
            story_id=story_id,
            interaction_type=InteractionType.QUESTION_REPLY,
            content=content,
        )
        return crud_interaction.create(session, obj_in=interaction_in)

    @staticmethod
    def submit_quiz_answer(
        session: SessionDep,
        story_id: uuid.UUID,
        user_id: uuid.UUID,
        option_selected: str,
    ) -> Dict[str, bool]:
        """Submit a quiz answer and return result"""
        # For now, return a mock result
        # TODO: Implement proper quiz logic with correct answers stored in story
        is_correct = True  # Mock result

        # Record the answer
        interaction_in = StoryInteractionCreate(
            story_id=story_id,
            interaction_type=InteractionType.QUIZ_ANSWER,
            option_selected=option_selected,
            is_correct=is_correct,
        )
        crud_interaction.create(session, obj_in=interaction_in)

        return {"is_correct": is_correct}

    @staticmethod
    def get_poll_results(session: SessionDep, story_id: uuid.UUID) -> Dict[str, int]:
        """Get poll results for a story"""
        return crud_interaction.get_poll_results(session, story_id=story_id)

    @staticmethod
    def get_question_replies(
        session: SessionDep,
        story_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryInteraction]:
        """Get question replies for a story"""
        return crud_interaction.get_story_interactions(
            session,
            story_id=story_id,
            interaction_type=InteractionType.QUESTION_REPLY,
            skip=skip,
            limit=limit,
        )


story_interaction_service = StoryInteractionService()
