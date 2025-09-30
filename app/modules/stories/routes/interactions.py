import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.stories.model.interaction import InteractionType
from app.modules.stories.schema.interaction import (
    PollVoteCreate,
    QuestionReplyCreate,
    QuizAnswerCreate,
    QuizResult,
    StoryInteractionCreate,
    StoryInteractionPublic,
    StoryInteractionUpdate,
)
from app.modules.stories.services.interaction_service import story_interaction_service
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter(prefix="/interactions", tags=["story-interactions"])


@router.get("/story/{story_id}", response_model=List[StoryInteractionPublic])
def get_story_interactions(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
    interaction_type: Optional[InteractionType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get interactions for a specific story
    """
    interactions = story_interaction_service.get_story_interactions(
        session=session,
        story_id=story_id,
        interaction_type=interaction_type,
        skip=skip,
        limit=limit,
    )
    return interactions


@router.post(
    "/", response_model=StoryInteractionPublic, status_code=status.HTTP_201_CREATED
)
def create_interaction(
    session: SessionDep,
    current_user: CurrentUser,
    interaction_in: StoryInteractionCreate,
) -> Any:
    """
    Create a new story interaction
    """
    interaction = story_interaction_service.create_interaction(
        session=session,
        interaction_in=interaction_in,
        user_id=current_user.id,
    )
    return interaction


@router.put("/{interaction_id}", response_model=StoryInteractionPublic)
def update_interaction(
    session: SessionDep,
    current_user: CurrentUser,
    interaction_id: uuid.UUID,
    interaction_in: StoryInteractionUpdate,
) -> Any:
    """
    Update an interaction
    """
    interaction = story_interaction_service.get_interaction(
        session=session, interaction_id=interaction_id
    )
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )

    if interaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this interaction",
        )

    updated_interaction = story_interaction_service.update_interaction(
        session=session,
        interaction_id=interaction_id,
        interaction_in=interaction_in,
    )
    if not updated_interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )
    return updated_interaction


@router.delete("/{interaction_id}", response_model=Message)
def delete_interaction(
    session: SessionDep,
    current_user: CurrentUser,
    interaction_id: uuid.UUID,
) -> Any:
    """
    Delete an interaction
    """
    interaction = story_interaction_service.get_interaction(
        session=session, interaction_id=interaction_id
    )
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )

    if interaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this interaction",
        )

    deleted = story_interaction_service.delete_interaction(
        session=session, interaction_id=interaction_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )

    return Message(message="Interaction deleted successfully")


# Poll endpoints
@router.post(
    "/poll/vote",
    response_model=StoryInteractionPublic,
    status_code=status.HTTP_201_CREATED,
)
def vote_poll(
    session: SessionDep,
    current_user: CurrentUser,
    vote_in: PollVoteCreate,
) -> Any:
    """
    Vote in a poll
    """
    interaction = story_interaction_service.vote_poll(
        session=session,
        story_id=vote_in.story_id,
        user_id=current_user.id,
        option_selected=vote_in.option_selected,
    )
    return interaction


@router.get("/poll/{story_id}/results", response_model=Dict[str, int])
def get_poll_results(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
) -> Any:
    """
    Get poll results for a story
    """
    results = story_interaction_service.get_poll_results(
        session=session, story_id=story_id
    )
    return results


# Question endpoints
@router.post(
    "/question/reply",
    response_model=StoryInteractionPublic,
    status_code=status.HTTP_201_CREATED,
)
def submit_question_reply(
    session: SessionDep,
    current_user: CurrentUser,
    reply_in: QuestionReplyCreate,
) -> Any:
    """
    Submit a reply to a question
    """
    interaction = story_interaction_service.submit_question_reply(
        session=session,
        story_id=reply_in.story_id,
        user_id=current_user.id,
        content=reply_in.content,
    )
    return interaction


@router.get("/question/{story_id}/replies", response_model=List[StoryInteractionPublic])
def get_question_replies(
    session: SessionDep,
    current_user: CurrentUser,
    story_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Get question replies for a story
    """
    replies = story_interaction_service.get_question_replies(
        session=session,
        story_id=story_id,
        skip=skip,
        limit=limit,
    )
    return replies


# Quiz endpoints
@router.post("/quiz/answer", response_model=QuizResult)
def submit_quiz_answer(
    session: SessionDep,
    current_user: CurrentUser,
    answer_in: QuizAnswerCreate,
) -> Any:
    """
    Submit a quiz answer
    """
    result = story_interaction_service.submit_quiz_answer(
        session=session,
        story_id=answer_in.story_id,
        user_id=current_user.id,
        option_selected=answer_in.option_selected,
    )
    return result
