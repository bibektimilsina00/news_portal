from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.messaging.crud.crud_participant import crud_participant
from app.modules.messaging.model.participant import (
    ConversationParticipant,
    ParticipantRole,
)
from app.modules.messaging.schema.participant import (
    ConversationParticipantCreate,
)


class ParticipantService:
    """Business logic for conversation participants"""

    @staticmethod
    def add_participant(
        session: Session, conversation_id: UUID, user_id: UUID, role: str = "member"
    ) -> Optional[ConversationParticipant]:
        """Add a participant to a conversation"""
        # Check if already a participant
        existing = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if existing:
            return existing

        # Create participant
        participant_data = ConversationParticipantCreate(
            conversation_id=conversation_id, user_id=user_id, role=ParticipantRole(role)
        )

        return crud_participant.create(session, obj_in=participant_data)

    @staticmethod
    def get_participant(
        session: Session, participant_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Get participant by ID"""
        return crud_participant.get(session, participant_id)

    @staticmethod
    def get_conversation_participants(
        session: Session, conversation_id: UUID
    ) -> list[ConversationParticipant]:
        """Get all participants in a conversation"""
        return crud_participant.get_by_conversation(session, conversation_id)

    @staticmethod
    def get_user_participations(
        session: Session, user_id: UUID
    ) -> list[ConversationParticipant]:
        """Get all conversations a user participates in"""
        return crud_participant.get_by_user(session, user_id)

    @staticmethod
    def update_participant_role(
        session: Session, participant_id: UUID, new_role: str, updater_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Update participant role"""
        participant = crud_participant.get(session, participant_id)
        if not participant:
            return None

        # Check permissions (only owner can change roles)
        updater = crud_participant.get_by_user_and_conversation(
            session, updater_id, participant.conversation_id
        )
        if not updater or updater.role.value != "owner":
            return None

        return crud_participant.update_role(session, participant_id, new_role)

    @staticmethod
    def update_participant_status(
        session: Session, participant_id: UUID, new_status: str, updater_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Update participant status (admin/moderator action)"""
        participant = crud_participant.get(session, participant_id)
        if not participant:
            return None

        # Check permissions
        updater = crud_participant.get_by_user_and_conversation(
            session, updater_id, participant.conversation_id
        )
        if not updater:
            return None

        can_moderate = (
            updater.role.value in ["owner", "admin"]
            or updater.can_moderate_participants
        )

        if not can_moderate:
            return None

        return crud_participant.update_status(session, participant_id, new_status)

    @staticmethod
    def remove_participant(
        session: Session, conversation_id: UUID, user_id: UUID, remover_id: UUID
    ) -> bool:
        """Remove a participant from a conversation"""
        # Check permissions
        remover = crud_participant.get_by_user_and_conversation(
            session, remover_id, conversation_id
        )
        if not remover:
            return False

        target = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not target:
            return False

        can_remove = (
            user_id == remover_id  # Self-removal
            or remover.role.value == "owner"  # Owner can remove anyone
            or (
                remover.role.value == "admin"
                and target.role.value not in ["owner", "admin"]
            )  # Admin can remove non-admins
            or remover.can_remove_participants  # Has removal permission
        )

        if not can_remove:
            return False

        return crud_participant.remove_participant(session, conversation_id, user_id)

    @staticmethod
    def mute_participant(
        session: Session,
        participant_id: UUID,
        muted_until: Optional[datetime],
        muter_id: UUID,
    ) -> Optional[ConversationParticipant]:
        """Mute a participant"""
        participant = crud_participant.get(session, participant_id)
        if not participant:
            return None

        # Check permissions
        muter = crud_participant.get_by_user_and_conversation(
            session, muter_id, participant.conversation_id
        )
        if not muter:
            return None

        can_mute = muter.role.value in ["owner", "admin"]

        if not can_mute:
            return None

        return crud_participant.mute_participant_with_duration(
            session, participant_id, muted_until
        )

    @staticmethod
    def unmute_participant(
        session: Session, participant_id: UUID, unmuter_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Unmute a participant"""
        participant = crud_participant.get(session, participant_id)
        if not participant:
            return None

        # Check permissions
        unmuter = crud_participant.get_by_user_and_conversation(
            session, unmuter_id, participant.conversation_id
        )
        if not unmuter:
            return None

        can_unmute = unmuter.role.value in ["owner", "admin"]

        if not can_unmute:
            return None

        return crud_participant.unmute_participant(session, participant_id)

    @staticmethod
    def update_last_seen(
        session: Session, conversation_id: UUID, user_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Update participant's last seen timestamp"""
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return None

        return crud_participant.update_last_seen(session, participant.id)

    @staticmethod
    def update_notification_settings(
        session: Session, participant_id: UUID, settings: dict, user_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Update participant's notification settings"""
        participant = crud_participant.get(session, participant_id)
        if not participant:
            return None

        # Only the participant themselves can update their settings
        if participant.user_id != user_id:
            return None

        return crud_participant.update_notification_settings(
            session, participant_id, settings
        )

    @staticmethod
    def get_participant_permissions(
        session: Session, conversation_id: UUID, user_id: UUID
    ) -> dict:
        """Get participant's permissions in a conversation"""
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return {}

        return {
            "role": participant.role.value,
            "status": participant.status.value,
            "can_send_messages": participant.can_send_messages,
            "can_add_participants": participant.can_add_participants,
            "can_remove_participants": participant.can_remove_participants,
            "can_delete_messages": participant.can_delete_messages,
            "can_moderate": participant.can_moderate,
            "can_change_settings": participant.can_change_settings,
            "is_muted": participant.status.value == "muted",
            "muted_until": None,  # Not implemented in model
        }

    @staticmethod
    def get_unread_count(session: Session, conversation_id: UUID, user_id: UUID) -> int:
        """Get unread message count for a participant"""
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return 0

        return participant.unread_count

    @staticmethod
    def reset_unread_count(
        session: Session, conversation_id: UUID, user_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Reset unread message count for a participant"""
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return None

        return crud_participant.reset_unread_count(session, participant.id)

    @staticmethod
    def ban_participant(
        session: Session, participant_id: UUID, reason: Optional[str], banner_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Ban a participant from the conversation"""
        participant = crud_participant.get(session, participant_id)
        if not participant:
            return None

        # Check permissions
        banner = crud_participant.get_by_user_and_conversation(
            session, banner_id, participant.conversation_id
        )
        if not banner:
            return None

        can_ban = banner.role.value in ["owner", "admin"]

        if not can_ban:
            return None

        return crud_participant.ban_participant_with_reason(
            session, participant_id, reason
        )

    @staticmethod
    def unban_participant(
        session: Session, participant_id: UUID, unbanned_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Unban a participant"""
        participant = crud_participant.get(session, participant_id)
        if not participant:
            return None

        # Check permissions
        unbanned = crud_participant.get_by_user_and_conversation(
            session, unbanned_id, participant.conversation_id
        )
        if not unbanned:
            return None

        can_unban = unbanned.role.value in ["owner", "admin"]

        if not can_unban:
            return None

        return crud_participant.unban_participant(session, participant_id)


participant_service = ParticipantService()
