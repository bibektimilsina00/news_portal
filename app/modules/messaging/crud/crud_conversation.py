from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.messaging.model.conversation import Conversation
from app.modules.messaging.schema.conversation import (
    ConversationCreate,
    ConversationUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    """CRUD operations for conversations"""

    def get_by_participant(self, session: Session, user_id: UUID) -> list[Conversation]:
        """Get all conversations for a user"""
        # This would require joining with participants table
        # For now, return empty list - will be implemented with proper relationships
        return []

    def get_direct_conversation(
        self, session: Session, user1_id: UUID, user2_id: UUID
    ) -> Optional[Conversation]:
        """Get direct conversation between two users"""
        # This would require complex query with participants
        # For now, return None - will be implemented with proper relationships
        return None

    def get_group_conversations(
        self, session: Session, creator_id: UUID
    ) -> list[Conversation]:
        """Get group conversations created by a user"""
        return list(
            session.exec(
                select(Conversation).where(
                    Conversation.creator_id == creator_id, Conversation.is_group == True
                )
            ).all()
        )

    def get_active_conversations(self, session: Session) -> list[Conversation]:
        """Get all active conversations"""
        from app.modules.messaging.model.conversation import ConversationStatus

        return list(
            session.exec(
                select(Conversation).where(
                    Conversation.status == ConversationStatus.active
                )
            ).all()
        )

    def update_last_message(
        self,
        session: Session,
        conversation_id: UUID,
        message_preview: str,
        message_at: datetime,
    ) -> Optional[Conversation]:
        """Update conversation's last message info"""
        from datetime import datetime

        conversation = self.get(session, conversation_id)
        if conversation:
            conversation.last_message_preview = message_preview
            conversation.last_message_at = message_at
            conversation.message_count += 1
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation

    def update_participant_count(
        self, session: Session, conversation_id: UUID, count: int
    ) -> Optional[Conversation]:
        """Update participant count"""
        conversation = self.get(session, conversation_id)
        if conversation:
            conversation.participant_count = count
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation

    def archive_conversation(
        self, session: Session, conversation_id: UUID
    ) -> Optional[Conversation]:
        """Archive a conversation"""
        from app.modules.messaging.model.conversation import ConversationStatus

        conversation = self.get(session, conversation_id)
        if conversation:
            conversation.status = ConversationStatus.archived
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation

    def unarchive_conversation(
        self, session: Session, conversation_id: UUID
    ) -> Optional[Conversation]:
        """Unarchive a conversation"""
        from app.modules.messaging.model.conversation import ConversationStatus

        conversation = self.get(session, conversation_id)
        if conversation:
            conversation.status = ConversationStatus.active
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation

    def delete_conversation(
        self, session: Session, conversation_id: UUID
    ) -> Optional[Conversation]:
        """Soft delete a conversation"""
        from app.modules.messaging.model.conversation import ConversationStatus

        conversation = self.get(session, conversation_id)
        if conversation:
            conversation.status = ConversationStatus.deleted
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation

    def get_by_user_id(self, session: Session, user_id: UUID) -> list[Conversation]:
        """Get conversations created by a user"""
        return list(
            session.exec(
                select(Conversation).where(Conversation.creator_id == user_id)
            ).all()
        )


crud_conversation = CRUDConversation(Conversation)
