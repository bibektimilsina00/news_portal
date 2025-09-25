from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.modules.messaging.crud.crud_conversation import crud_conversation
from app.modules.messaging.schema.conversation import (
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
)
from app.modules.messaging.services.conversation_service import conversation_service
from app.modules.messaging.services.participant_service import participant_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=ConversationPublic)
def create_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_in: ConversationCreate,
) -> ConversationPublic:
    """Create a new conversation"""
    conversation = conversation_service.create_conversation(
        session, current_user.id, conversation_in
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create conversation",
        )
    return ConversationPublic.model_validate(conversation)


@router.get("/", response_model=List[ConversationPublic])
def read_conversations(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> List[ConversationPublic]:
    """Get user's conversations"""
    conversations = conversation_service.get_user_conversations(
        session, current_user.id
    )
    return [
        ConversationPublic.model_validate(c) for c in conversations[skip : skip + limit]
    ]


@router.get("/{conversation_id}", response_model=ConversationPublic)
def read_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> ConversationPublic:
    """Get conversation by ID"""
    conversation = conversation_service.get_conversation(session, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    # Check if user is participant
    participant = participant_service.get_participant_permissions(
        session, conversation_id, current_user.id
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    return ConversationPublic.model_validate(conversation)


@router.put("/{conversation_id}", response_model=ConversationPublic)
def update_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
    conversation_in: ConversationUpdate,
) -> ConversationPublic:
    """Update conversation details"""
    conversation = conversation_service.update_conversation(
        session, conversation_id, conversation_in, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this conversation",
        )
    return ConversationPublic.model_validate(conversation)


@router.delete("/{conversation_id}")
def delete_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> dict:
    """Delete a conversation"""
    success = conversation_service.delete_conversation(
        session, conversation_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this conversation",
        )
    return {"message": "Conversation deleted successfully"}


@router.post("/{conversation_id}/archive")
def archive_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> dict:
    """Archive a conversation"""
    conversation = conversation_service.archive_conversation(
        session, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive this conversation",
        )
    return {"message": "Conversation archived successfully"}


@router.post("/{conversation_id}/unarchive")
def unarchive_conversation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> dict:
    """Unarchive a conversation"""
    conversation = conversation_service.unarchive_conversation(
        session, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to unarchive this conversation",
        )
    return {"message": "Conversation unarchived successfully"}


@router.post("/{conversation_id}/participants", response_model=dict)
def add_participants(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
    user_ids: List[UUID],
) -> dict:
    """Add participants to a conversation"""
    added = conversation_service.add_participants(
        session, conversation_id, user_ids, current_user.id
    )
    if not added:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add participants",
        )
    return {"added_participants": added}


@router.delete("/{conversation_id}/participants/{user_id}")
def remove_participant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
    user_id: UUID,
) -> dict:
    """Remove a participant from a conversation"""
    success = conversation_service.remove_participant(
        session, conversation_id, user_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove this participant",
        )
    return {"message": "Participant removed successfully"}


@router.get("/{conversation_id}/participants")
def get_conversation_participants(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> List[dict]:
    """Get participants in a conversation"""
    # Check if user is participant
    participant = participant_service.get_participant_permissions(
        session, conversation_id, current_user.id
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    participants = conversation_service.get_conversation_participants(
        session, conversation_id
    )
    return participants


@router.put("/{conversation_id}/participants/{participant_id}/role")
def update_participant_role(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
    participant_id: UUID,
    role: str,
) -> dict:
    """Update participant role"""
    updated = conversation_service.update_participant_role(
        session, conversation_id, participant_id, role, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update participant role",
        )
    return {"participant_id": updated["participant_id"], "role": updated["role"]}
