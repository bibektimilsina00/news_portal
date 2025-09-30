from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.messaging.model.participant import ConversationParticipant
from app.modules.messaging.schema.participant import (
    ConversationParticipantCreate,
    ConversationParticipantUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDConversationParticipant(
    CRUDBase[
        ConversationParticipant,
        ConversationParticipantCreate,
        ConversationParticipantUpdate,
    ]
):
    """CRUD operations for conversation participants"""

    def get_by_conversation(
        self, session: Session, conversation_id: UUID
    ) -> list[ConversationParticipant]:
        """Get all participants for a conversation"""
        return list(
            session.exec(
                select(ConversationParticipant).where(
                    ConversationParticipant.conversation_id == conversation_id
                )
            ).all()
        )

    def get_by_user_and_conversation(
        self, session: Session, user_id: UUID, conversation_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Get participant record for specific user and conversation"""
        return session.exec(
            select(ConversationParticipant).where(
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.conversation_id == conversation_id,
            )
        ).first()

    def get_active_participants(
        self, session: Session, conversation_id: UUID
    ) -> list[ConversationParticipant]:
        """Get active participants for a conversation"""
        from app.modules.messaging.model.participant import ParticipantStatus

        return list(
            session.exec(
                select(ConversationParticipant).where(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.status == ParticipantStatus.active,
                )
            ).all()
        )

    def get_admins(
        self, session: Session, conversation_id: UUID
    ) -> list[ConversationParticipant]:
        """Get admin participants for a conversation"""
        from app.modules.messaging.model.participant import ParticipantRole

        return list(
            session.exec(
                select(ConversationParticipant).where(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.role.in_(
                        [ParticipantRole.admin, ParticipantRole.owner]
                    ),
                )
            ).all()
        )

    def add_participant(
        self,
        session: Session,
        conversation_id: UUID,
        user_id: UUID,
        role: str = "member",
    ) -> ConversationParticipant:
        """Add a user to a conversation"""
        from app.modules.messaging.model.participant import ParticipantRole

        # Check if user is already a participant
        existing = self.get_by_user_and_conversation(session, user_id, conversation_id)
        if existing:
            # Re-activate if they left
            if existing.status == "left":
                existing.status = "active"
                existing.joined_at = datetime.utcnow()
                existing.left_at = None
                session.add(existing)
                session.commit()
                session.refresh(existing)
            return existing

        # Create new participant
        participant_data = ConversationParticipantCreate(
            conversation_id=conversation_id,
            user_id=user_id,
            role=ParticipantRole(role),
            joined_at=datetime.utcnow(),
        )
        return self.create(session, obj_in=participant_data)

    def remove_participant(
        self, session: Session, conversation_id: UUID, user_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Remove a user from a conversation"""
        from app.modules.messaging.model.participant import ParticipantStatus

        participant = self.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if participant:
            participant.status = ParticipantStatus.left
            participant.left_at = datetime.utcnow()
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def update_role(
        self, session: Session, participant_id: UUID, new_role: str
    ) -> Optional[ConversationParticipant]:
        """Update participant role"""
        from app.modules.messaging.model.participant import ParticipantRole

        participant = self.get(session, participant_id)
        if participant:
            participant.role = ParticipantRole(new_role)
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def mute_participant(
        self, session: Session, participant_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Mute a participant"""
        from app.modules.messaging.model.participant import ParticipantStatus

        participant = self.get(session, participant_id)
        if participant:
            participant.status = ParticipantStatus.muted
            # Note: muted_until field doesn't exist in model, using status instead
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def unmute_participant(
        self, session: Session, participant_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Unmute a participant"""
        from app.modules.messaging.model.participant import ParticipantStatus

        participant = self.get(session, participant_id)
        if participant:
            participant.status = ParticipantStatus.active
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def ban_participant(
        self, session: Session, participant_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Ban a participant"""
        from app.modules.messaging.model.participant import ParticipantStatus

        participant = self.get(session, participant_id)
        if participant:
            participant.status = ParticipantStatus.banned
            participant.left_at = datetime.utcnow()
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def unban_participant(
        self, session: Session, participant_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Unban a participant"""
        from app.modules.messaging.model.participant import ParticipantStatus

        participant = self.get(session, participant_id)
        if participant:
            participant.status = ParticipantStatus.active
            participant.left_at = None
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def update_last_seen(
        self, session: Session, participant_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Update participant's last seen timestamp"""
        participant = self.get(session, participant_id)
        if participant:
            participant.last_seen_at = datetime.utcnow()
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def update_unread_count(
        self, session: Session, conversation_id: UUID, user_id: UUID, count: int
    ) -> Optional[ConversationParticipant]:
        """Update unread message count for a participant"""
        participant = self.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if participant:
            participant.unread_count = max(0, count)
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def mark_messages_read(
        self,
        session: Session,
        conversation_id: UUID,
        user_id: UUID,
        last_read_message_id: UUID,
    ) -> Optional[ConversationParticipant]:
        """Mark messages as read for a participant"""
        participant = self.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if participant:
            participant.last_read_message_id = last_read_message_id
            participant.unread_count = 0
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def get_by_user(
        self, session: Session, user_id: UUID
    ) -> list[ConversationParticipant]:
        """Get all participations for a user"""
        return list(
            session.exec(
                select(ConversationParticipant).where(
                    ConversationParticipant.user_id == user_id
                )
            ).all()
        )

    def update_status(
        self, session: Session, participant_id: UUID, new_status: str
    ) -> Optional[ConversationParticipant]:
        """Update participant status"""
        from app.modules.messaging.model.participant import ParticipantStatus

        participant = self.get(session, participant_id)
        if participant:
            participant.status = ParticipantStatus(new_status)
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def mute_participant_with_duration(
        self,
        session: Session,
        participant_id: UUID,
        muted_until: Optional[datetime] = None,
    ) -> Optional[ConversationParticipant]:
        """Mute a participant until a specific time"""
        from app.modules.messaging.model.participant import ParticipantStatus

        participant = self.get(session, participant_id)
        if participant:
            participant.status = ParticipantStatus.muted
            # Note: muted_until field doesn't exist in model, using status instead
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def update_notification_settings(
        self, session: Session, participant_id: UUID, settings: dict
    ) -> Optional[ConversationParticipant]:
        """Update notification settings"""
        participant = self.get(session, participant_id)
        if participant:
            if "notifications_enabled" in settings:
                participant.notifications_enabled = settings["notifications_enabled"]
            if "notification_sound" in settings:
                participant.notification_sound = settings["notification_sound"]
            if "notification_preview" in settings:
                participant.notification_preview = settings["notification_preview"]
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def reset_unread_count(
        self, session: Session, participant_id: UUID
    ) -> Optional[ConversationParticipant]:
        """Reset unread count for a participant"""
        participant = self.get(session, participant_id)
        if participant:
            participant.unread_count = 0
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant

    def ban_participant_with_reason(
        self, session: Session, participant_id: UUID, reason: Optional[str] = None
    ) -> Optional[ConversationParticipant]:
        """Ban a participant"""
        from app.modules.messaging.model.participant import ParticipantStatus

        participant = self.get(session, participant_id)
        if participant:
            participant.status = ParticipantStatus.banned
            participant.left_at = datetime.utcnow()
            session.add(participant)
            session.commit()
            session.refresh(participant)
        return participant


crud_participant = CRUDConversationParticipant(ConversationParticipant)
