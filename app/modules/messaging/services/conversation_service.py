from typing import Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.messaging.crud.crud_conversation import crud_conversation
from app.modules.messaging.crud.crud_participant import crud_participant
from app.modules.messaging.model.conversation import Conversation
from app.modules.messaging.schema.conversation import (
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
)


class ConversationService:
    """Business logic for conversations"""

    @staticmethod
    def create_conversation(
        session: Session, creator_id: UUID, conversation_data: ConversationCreate
    ) -> Conversation:
        """Create a new conversation"""
        # Determine if it's a group conversation
        is_group = (
            len(conversation_data.participant_ids) > 2
            or conversation_data.title is not None
        )

        # Create conversation data
        conversation_dict = conversation_data.model_dump()
        conversation_dict.pop("participant_ids")  # Remove from conversation data
        conversation_dict["creator_id"] = creator_id
        conversation_dict["is_group"] = is_group

        # Create ConversationCreate object
        conversation_create = ConversationCreate(**conversation_dict)
        conversation = crud_conversation.create(session, obj_in=conversation_create)

        # Add participants
        participants = [creator_id] + conversation_data.participant_ids
        unique_participants = list(set(participants))  # Remove duplicates

        for user_id in unique_participants:
            role = "owner" if user_id == creator_id else "member"
            crud_participant.add_participant(session, conversation.id, user_id, role)

        # Update participant count
        crud_conversation.update_participant_count(
            session, conversation.id, len(unique_participants)
        )

        return conversation

    @staticmethod
    def get_conversation(
        session: Session, conversation_id: UUID
    ) -> Optional[Conversation]:
        """Get conversation by ID"""
        return crud_conversation.get(session, conversation_id)

    @staticmethod
    def get_user_conversations(session: Session, user_id: UUID) -> list[Conversation]:
        """Get all conversations for a user"""
        # This would require joining with participants table
        # For now, return conversations where user is creator
        return crud_conversation.get_by_user_id(session, user_id)

    @staticmethod
    def update_conversation(
        session: Session,
        conversation_id: UUID,
        update_data: ConversationUpdate,
        user_id: UUID,
    ) -> Optional[Conversation]:
        """Update conversation details"""
        conversation = crud_conversation.get(session, conversation_id)
        if not conversation:
            return None

        # Check permissions (only creator or admins can update)
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant or not participant.can_change_settings:
            return None

        return crud_conversation.update(
            session, db_obj=conversation, obj_in=update_data
        )

    @staticmethod
    def delete_conversation(
        session: Session, conversation_id: UUID, user_id: UUID
    ) -> bool:
        """Delete a conversation"""
        conversation = crud_conversation.get(session, conversation_id)
        if not conversation:
            return False

        # Check permissions (only creator can delete)
        if conversation.creator_id != user_id:
            return False

        crud_conversation.delete_conversation(session, conversation_id)
        return True

    @staticmethod
    def archive_conversation(
        session: Session, conversation_id: UUID, user_id: UUID
    ) -> Optional[Conversation]:
        """Archive a conversation for a user"""
        # Check if user is participant
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return None

        return crud_conversation.archive_conversation(session, conversation_id)

    @staticmethod
    def unarchive_conversation(
        session: Session, conversation_id: UUID, user_id: UUID
    ) -> Optional[Conversation]:
        """Unarchive a conversation for a user"""
        # Check if user is participant
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return None

        return crud_conversation.unarchive_conversation(session, conversation_id)

    @staticmethod
    def add_participants(
        session: Session, conversation_id: UUID, user_ids: list[UUID], adder_id: UUID
    ) -> list[dict]:
        """Add participants to a conversation"""
        conversation = crud_conversation.get(session, conversation_id)
        if not conversation:
            return []

        # Check permissions
        adder_participant = crud_participant.get_by_user_and_conversation(
            session, adder_id, conversation_id
        )
        if not adder_participant or not adder_participant.can_add_participants:
            return []

        # Check group limits
        current_count = conversation.participant_count
        if (
            conversation.max_participants
            and current_count + len(user_ids) > conversation.max_participants
        ):
            return []

        added_participants = []
        for user_id in user_ids:
            participant = crud_participant.add_participant(
                session, conversation_id, user_id
            )
            added_participants.append(
                {
                    "user_id": user_id,
                    "participant_id": participant.id,
                    "role": participant.role.value,
                }
            )

        # Update participant count
        crud_conversation.update_participant_count(
            session, conversation_id, current_count + len(added_participants)
        )

        return added_participants

    @staticmethod
    def remove_participant(
        session: Session, conversation_id: UUID, user_id: UUID, remover_id: UUID
    ) -> bool:
        """Remove a participant from a conversation"""
        conversation = crud_conversation.get(session, conversation_id)
        if not conversation:
            return False

        # Check permissions
        remover_participant = crud_participant.get_by_user_and_conversation(
            session, remover_id, conversation_id
        )
        if not remover_participant:
            return False

        # Can remove if: self-removal, admin rights, or removing someone else as admin
        target_participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not target_participant:
            return False

        can_remove = (
            user_id == remover_id  # Self-removal
            or remover_participant.can_remove_participants  # Admin permission
            or remover_participant.role.value == "owner"  # Owner can remove anyone
        )

        if not can_remove:
            return False

        removed = crud_participant.remove_participant(session, conversation_id, user_id)
        if removed:
            # Update participant count
            crud_conversation.update_participant_count(
                session, conversation_id, conversation.participant_count - 1
            )

        return removed is not None

    @staticmethod
    def get_conversation_participants(
        session: Session, conversation_id: UUID
    ) -> list[dict]:
        """Get participants for a conversation"""
        participants = crud_participant.get_by_conversation(session, conversation_id)
        return [
            {
                "id": p.id,
                "user_id": p.user_id,
                "role": p.role.value,
                "status": p.status.value,
                "joined_at": p.joined_at,
                "last_seen_at": p.last_seen_at,
            }
            for p in participants
        ]

    @staticmethod
    def update_participant_role(
        session: Session,
        conversation_id: UUID,
        participant_id: UUID,
        new_role: str,
        updater_id: UUID,
    ) -> Optional[dict]:
        """Update participant role"""
        # Check permissions (only owner can change roles)
        conversation = crud_conversation.get(session, conversation_id)
        if not conversation or conversation.creator_id != updater_id:
            return None

        updated = crud_participant.update_role(session, participant_id, new_role)
        if updated:
            return {
                "participant_id": updated.id,
                "user_id": updated.user_id,
                "role": updated.role.value,
            }
        return None


conversation_service = ConversationService()
