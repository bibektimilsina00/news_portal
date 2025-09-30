from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.modules.messaging.schema.message import (
    MessageCreate,
    MessagePublic,
    MessageUpdate,
)
from app.modules.messaging.services.message_service import message_service
from app.modules.messaging.services.participant_service import participant_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=MessagePublic)
def send_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_in: MessageCreate,
) -> MessagePublic:
    """Send a new message"""
    message = message_service.send_message(session, current_user.id, message_in)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to send message in this conversation",
        )
    return MessagePublic.model_validate(message)


@router.get("/{message_id}", response_model=MessagePublic)
def read_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: UUID,
) -> MessagePublic:
    """Get message by ID"""
    message = message_service.get_message(session, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    # Check if user is participant in conversation
    participant = participant_service.get_participant_permissions(
        session, message.conversation_id, current_user.id
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this message",
        )

    return MessagePublic.model_validate(message)


@router.get("/conversation/{conversation_id}", response_model=List[MessagePublic])
def read_conversation_messages(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[MessagePublic]:
    """Get messages in a conversation"""
    messages = message_service.get_conversation_messages(
        session, conversation_id, current_user.id, skip, limit
    )
    return [MessagePublic.model_validate(m) for m in messages]


@router.put("/{message_id}", response_model=MessagePublic)
def update_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: UUID,
    message_in: MessageUpdate,
) -> MessagePublic:
    """Update a message"""
    message = message_service.update_message(
        session, message_id, message_in, current_user.id
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this message",
        )
    return MessagePublic.model_validate(message)


@router.delete("/{message_id}")
def delete_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: UUID,
) -> dict:
    """Delete a message"""
    success = message_service.delete_message(session, message_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this message",
        )
    return {"message": "Message deleted successfully"}


@router.post("/{message_id}/read")
def mark_message_read(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: UUID,
) -> dict:
    """Mark a message as read"""
    success = message_service.mark_message_read(session, message_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mark this message as read",
        )
    return {"message": "Message marked as read"}


@router.post("/conversation/{conversation_id}/read")
def mark_conversation_read(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> dict:
    """Mark all messages in conversation as read"""
    success = message_service.mark_conversation_read(
        session, conversation_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )
    return {"message": "Conversation marked as read"}


@router.post("/{message_id}/reactions")
def add_reaction(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: UUID,
    emoji: str,
) -> dict:
    """Add reaction to a message"""
    message = message_service.add_reaction(session, message_id, current_user.id, emoji)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to react to this message",
        )
    return {"message": "Reaction added successfully"}


@router.delete("/{message_id}/reactions/{emoji}")
def remove_reaction(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: UUID,
    emoji: str,
) -> dict:
    """Remove reaction from a message"""
    message = message_service.remove_reaction(
        session, message_id, current_user.id, emoji
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction not found"
        )
    return {"message": "Reaction removed successfully"}


@router.get("/{message_id}/reactions")
def get_message_reactions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: UUID,
) -> dict:
    """Get reactions for a message"""
    # Check if user can access the message
    message = message_service.get_message(session, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    participant = participant_service.get_participant_permissions(
        session, message.conversation_id, current_user.id
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this message",
        )

    reactions = message_service.get_message_reactions(session, message_id)
    return reactions


@router.get("/search/{conversation_id}")
def search_messages(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
    q: str,
    skip: int = 0,
    limit: int = 50,
) -> List[MessagePublic]:
    """Search messages in a conversation"""
    messages = message_service.search_messages(
        session, conversation_id, current_user.id, q, skip, limit
    )
    return [MessagePublic.model_validate(m) for m in messages]


@router.post("/{message_id}/forward")
def forward_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_id: UUID,
    target_conversation_id: UUID,
) -> MessagePublic:
    """Forward a message to another conversation"""
    message = message_service.forward_message(
        session, message_id, target_conversation_id, current_user.id
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to forward this message",
        )
    return MessagePublic.model_validate(message)


@router.post("/schedule")
def schedule_message(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    message_in: MessageCreate,
    scheduled_at: str,  # ISO format datetime string
) -> MessagePublic:
    """Schedule a message to be sent later"""
    from datetime import datetime

    try:
        scheduled_datetime = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format.",
        )

    message = message_service.schedule_message(
        session, current_user.id, message_in, scheduled_datetime
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to schedule message in this conversation",
        )
    return MessagePublic.model_validate(message)
