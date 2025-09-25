from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.messaging.model.message import Message
from app.modules.messaging.schema.message import MessageCreate, MessageUpdate
from app.shared.crud.base import CRUDBase


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    """CRUD operations for messages"""

    def get_by_conversation(
        self, session: Session, conversation_id: UUID, skip: int = 0, limit: int = 50
    ) -> list[Message]:
        """Get messages for a conversation"""
        return list(
            session.exec(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
            ).all()
        )

    def get_message(self, session: Session, message_id: UUID) -> Optional[Message]:
        """Get a specific message"""
        return session.exec(select(Message).where(Message.id == message_id)).first()

    def get_messages_after(
        self, session: Session, conversation_id: UUID, after_timestamp: datetime
    ) -> list[Message]:
        """Get messages after a specific timestamp"""
        return list(
            session.exec(
                select(Message)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.created_at > after_timestamp,
                )
                .order_by(Message.created_at.asc())
            ).all()
        )

    def get_messages_before(
        self,
        session: Session,
        conversation_id: UUID,
        before_timestamp: datetime,
        limit: int = 50,
    ) -> list[Message]:
        """Get messages before a specific timestamp"""
        return list(
            session.exec(
                select(Message)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.created_at < before_timestamp,
                )
                .order_by(Message.created_at.desc())
                .limit(limit)
            ).all()
        )

    def get_unread_messages(
        self,
        session: Session,
        conversation_id: UUID,
        user_id: UUID,
        last_read_id: Optional[UUID] = None,
    ) -> list[Message]:
        """Get unread messages for a user in a conversation"""
        query = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,  # Don't include own messages
        )

        if last_read_id:
            # Get messages after the last read message
            last_read_message = self.get(session, last_read_id)
            if last_read_message:
                query = query.where(Message.created_at > last_read_message.created_at)

        return list(session.exec(query.order_by(Message.created_at.asc())).all())

    def mark_as_delivered(self, session: Session, message_ids: List[UUID]) -> int:
        """Mark messages as delivered"""
        from app.modules.messaging.model.message import MessageStatus

        messages = session.exec(
            select(Message).where(Message.id.in_(message_ids))
        ).all()

        updated_count = 0
        for message in messages:
            if message.status == MessageStatus.SENT:
                message.status = MessageStatus.DELIVERED
                message.delivered_at = datetime.utcnow()
                updated_count += 1

        if updated_count > 0:
            session.commit()

        return updated_count

    def mark_as_read(
        self, session: Session, message_ids: List[UUID], user_id: UUID
    ) -> int:
        """Mark messages as read by a user"""
        from app.modules.messaging.model.message import MessageStatus

        messages = session.exec(
            select(Message).where(
                Message.id.in_(message_ids),
                Message.sender_id != user_id,  # Don't mark own messages as read
            )
        ).all()

        updated_count = 0
        for message in messages:
            if message.status in [MessageStatus.SENT, MessageStatus.DELIVERED]:
                message.status = MessageStatus.READ
                message.read_at = datetime.utcnow()
                updated_count += 1

        if updated_count > 0:
            session.commit()

        return updated_count

    def add_reaction(
        self, session: Session, message_id: UUID, emoji: str, user_id: UUID
    ) -> Optional[Message]:
        """Add a reaction to a message"""
        message = self.get(session, message_id)
        if message:
            # Check if user already reacted with this emoji
            existing_reaction = None
            for reaction in message.reactions:
                if reaction.get("emoji") == emoji:
                    existing_reaction = reaction
                    break

            if existing_reaction:
                # Add user to existing reaction
                users = existing_reaction.get("users", [])
                if str(user_id) not in users:
                    users.append(str(user_id))
                    existing_reaction["users"] = users
                    message.reaction_count += 1
            else:
                # Create new reaction
                message.reactions.append({"emoji": emoji, "users": [str(user_id)]})
                message.reaction_count += 1

            session.add(message)
            session.commit()
            session.refresh(message)

        return message

    def remove_reaction(
        self, session: Session, message_id: UUID, emoji: str, user_id: UUID
    ) -> Optional[Message]:
        """Remove a reaction from a message"""
        message = self.get(session, message_id)
        if message:
            for reaction in message.reactions:
                if reaction.get("emoji") == emoji:
                    users = reaction.get("users", [])
                    if str(user_id) in users:
                        users.remove(str(user_id))
                        if not users:
                            # Remove reaction if no users left
                            message.reactions.remove(reaction)
                        else:
                            reaction["users"] = users
                        message.reaction_count = max(0, message.reaction_count - 1)
                        break

            session.add(message)
            session.commit()
            session.refresh(message)

        return message

    def delete_message(self, session: Session, message_id: UUID) -> Optional[Message]:
        """Soft delete a message"""
        message = self.get(session, message_id)
        if message:
            message.is_deleted = True
            message.deleted_at = datetime.utcnow()
            session.add(message)
            session.commit()
            session.refresh(message)
        return message

    def search_messages(
        self,
        session: Session,
        query: str,
        conversation_id: Optional[UUID] = None,
        sender_id: Optional[UUID] = None,
        limit: int = 50,
    ) -> list[Message]:
        """Search messages by content"""
        # Basic text search - in production, this would use full-text search
        search_query = f"%{query}%"

        sql_query = select(Message).where(
            Message.content.ilike(search_query), Message.is_deleted == False
        )

        if conversation_id:
            sql_query = sql_query.where(Message.conversation_id == conversation_id)

        if sender_id:
            sql_query = sql_query.where(Message.sender_id == sender_id)

        return list(
            session.exec(
                sql_query.order_by(Message.created_at.desc()).limit(limit)
            ).all()
        )


crud_message = CRUDMessage(Message)
