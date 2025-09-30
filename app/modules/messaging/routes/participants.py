from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.modules.messaging.schema.participant import (
    ConversationParticipantPublic,
    ConversationParticipantUpdate,
)
from app.modules.messaging.services.participant_service import participant_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/{participant_id}", response_model=ConversationParticipantPublic)
def read_participant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
) -> ConversationParticipantPublic:
    """Get participant by ID"""
    participant = participant_service.get_participant(session, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )

    # Check if user can access this conversation
    permissions = participant_service.get_participant_permissions(
        session, participant.conversation_id, current_user.id
    )
    if not permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this participant",
        )

    return ConversationParticipantPublic.model_validate(participant)


@router.put("/{participant_id}", response_model=ConversationParticipantPublic)
def update_participant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
    participant_in: ConversationParticipantUpdate,
) -> ConversationParticipantPublic:
    """Update participant settings"""
    participant = participant_service.get_participant(session, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )

    # Only the participant themselves can update their own settings
    if participant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own participant settings",
        )

    # For now, we'll just return the participant as is
    # In a full implementation, you'd update the participant with participant_in
    return ConversationParticipantPublic.model_validate(participant)


@router.put("/{participant_id}/role")
def update_participant_role(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
    role: str,
) -> dict:
    """Update participant role (admin/owner only)"""
    updated = participant_service.update_participant_role(
        session, participant_id, role, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update participant role",
        )
    return {"participant_id": participant_id, "role": role}


@router.put("/{participant_id}/status")
def update_participant_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
    status: str,
) -> dict:
    """Update participant status (moderator action)"""
    updated = participant_service.update_participant_status(
        session, participant_id, status, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update participant status",
        )
    return {"participant_id": participant_id, "status": status}


@router.post("/{participant_id}/mute")
def mute_participant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
    muted_until: Optional[str] = None,  # ISO format datetime string
) -> dict:
    """Mute a participant"""
    from datetime import datetime

    muted_datetime = None
    if muted_until:
        try:
            muted_datetime = datetime.fromisoformat(muted_until.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid datetime format. Use ISO format.",
            )

    updated = participant_service.mute_participant(
        session, participant_id, muted_datetime, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mute this participant",
        )
    return {"participant_id": participant_id, "muted_until": muted_until}


@router.post("/{participant_id}/unmute")
def unmute_participant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
) -> dict:
    """Unmute a participant"""
    updated = participant_service.unmute_participant(
        session, participant_id, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to unmute this participant",
        )
    return {"participant_id": participant_id, "message": "Participant unmuted"}


@router.post("/{participant_id}/ban")
def ban_participant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
    reason: Optional[str] = None,
) -> dict:
    """Ban a participant from the conversation"""
    updated = participant_service.ban_participant(
        session, participant_id, reason, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to ban this participant",
        )
    return {"participant_id": participant_id, "message": "Participant banned"}


@router.post("/{participant_id}/unban")
def unban_participant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
) -> dict:
    """Unban a participant"""
    updated = participant_service.unban_participant(
        session, participant_id, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to unban this participant",
        )
    return {"participant_id": participant_id, "message": "Participant unbanned"}


@router.get("/conversation/{conversation_id}")
def get_conversation_participants(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> list[ConversationParticipantPublic]:
    """Get all participants in a conversation"""
    # Check if user is participant
    permissions = participant_service.get_participant_permissions(
        session, conversation_id, current_user.id
    )
    if not permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    participants = participant_service.get_conversation_participants(
        session, conversation_id
    )
    return [ConversationParticipantPublic.model_validate(p) for p in participants]


@router.get("/user/me")
def get_user_participations(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> list[ConversationParticipantPublic]:
    """Get all conversations the current user participates in"""
    participants = participant_service.get_user_participations(session, current_user.id)
    return [ConversationParticipantPublic.model_validate(p) for p in participants]


@router.get("/{participant_id}/permissions")
def get_participant_permissions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    participant_id: UUID,
) -> dict:
    """Get participant permissions"""
    participant = participant_service.get_participant(session, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )

    # Check if user can access this conversation
    permissions = participant_service.get_participant_permissions(
        session, participant.conversation_id, current_user.id
    )
    if not permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this participant",
        )

    return participant_service.get_participant_permissions(
        session, participant.conversation_id, participant.user_id
    )


@router.post("/conversation/{conversation_id}/last-seen")
def update_last_seen(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> dict:
    """Update last seen timestamp for current user in conversation"""
    updated = participant_service.update_last_seen(
        session, conversation_id, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this conversation",
        )
    return {"message": "Last seen updated"}


@router.get("/conversation/{conversation_id}/unread-count")
def get_unread_count(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> dict:
    """Get unread message count for current user in conversation"""
    count = participant_service.get_unread_count(
        session, conversation_id, current_user.id
    )
    return {"unread_count": count}


@router.post("/conversation/{conversation_id}/reset-unread")
def reset_unread_count(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    conversation_id: UUID,
) -> dict:
    """Reset unread message count for current user in conversation"""
    updated = participant_service.reset_unread_count(
        session, conversation_id, current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this conversation",
        )
    return {"message": "Unread count reset"}
