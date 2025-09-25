from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.messaging.crud.crud_conversation import crud_conversation
from app.modules.messaging.crud.crud_message import crud_message
from app.modules.messaging.crud.crud_participant import crud_participant
from app.modules.messaging.model.message import Message, MessageStatus
from app.modules.messaging.schema.message import (
    MessageCreate,
    MessagePublic,
    MessageUpdate,
)


class MessageService:
    """Business logic for messages"""

    @staticmethod
    def send_message(
        session: Session, sender_id: UUID, message_data: MessageCreate
    ) -> Optional[Message]:
        """Send a new message"""
        # Check if sender is participant in conversation
        participant = crud_participant.get_by_user_and_conversation(
            session, sender_id, message_data.conversation_id
        )
        if not participant or participant.status.value != "active":
            return None

        # Check if conversation allows sending (group settings)
        conversation = crud_conversation.get(session, message_data.conversation_id)
        if not conversation:
            return None

        if conversation.only_admins_can_send and not participant.can_send_messages:
            return None

        # Create message
        message_dict = message_data.model_dump()
        message_dict["sender_id"] = sender_id
        message_dict["status"] = MessageStatus.SENT

        message_create = MessageCreate(**message_dict)
        message = crud_message.create(session, obj_in=message_create)

        # Update conversation's last message
        if message:
            crud_conversation.update_last_message(
                session,
                message.conversation_id,
                message.content[:200] if message.content else "",
                message.created_at,
            )

        return message

    @staticmethod
    def get_message(session: Session, message_id: UUID) -> Optional[Message]:
        """Get message by ID"""
        return crud_message.get(session, message_id)

    @staticmethod
    def get_conversation_messages(
        session: Session,
        conversation_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Message]:
        """Get messages for a conversation"""
        # Check if user is participant
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return []

        return crud_message.get_by_conversation(session, conversation_id, skip, limit)

    @staticmethod
    def update_message(
        session: Session, message_id: UUID, update_data: MessageUpdate, user_id: UUID
    ) -> Optional[Message]:
        """Update a message"""
        message = crud_message.get(session, message_id)
        if not message:
            return None

        # Only sender can edit their own messages
        if message.sender_id != user_id:
            return None

        # Check if message can still be edited (time limit)
        if datetime.utcnow() - message.created_at > timedelta(minutes=15):
            return None

        return crud_message.update(session, db_obj=message, obj_in=update_data)

    @staticmethod
    def delete_message(session: Session, message_id: UUID, user_id: UUID) -> bool:
        """Delete a message"""
        message = crud_message.get(session, message_id)
        if not message:
            return False

        # Check permissions
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, message.conversation_id
        )
        if not participant:
            return False

        can_delete = (
            message.sender_id == user_id  # Own message
            or participant.can_delete_messages  # Admin permission
        )

        if not can_delete:
            return False

        crud_message.delete_message(session, message_id)
        return True

    @staticmethod
    def mark_message_read(session: Session, message_id: UUID, user_id: UUID) -> bool:
        """Mark a message as read"""
        message = crud_message.get(session, message_id)
        if not message:
            return False

        # Check if user is participant in conversation
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, message.conversation_id
        )
        if not participant:
            return False

        # Update read status for this user
        count = crud_message.mark_as_read(session, [message_id], user_id)
        return count > 0

    @staticmethod
    def mark_conversation_read(
        session: Session, conversation_id: UUID, user_id: UUID
    ) -> bool:
        """Mark all messages in conversation as read for user"""
        # Check if user is participant
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return False

        # Get unread messages and mark them as read
        unread_messages = crud_message.get_unread_messages(
            session, conversation_id, user_id
        )
        if unread_messages:
            message_ids = [msg.id for msg in unread_messages]
            crud_message.mark_as_read(session, message_ids, user_id)

        return True

    @staticmethod
    def add_reaction(
        session: Session, message_id: UUID, user_id: UUID, emoji: str
    ) -> Optional[Message]:
        """Add reaction to a message"""
        message = crud_message.get(session, message_id)
        if not message:
            return None

        # Check if user is participant in conversation
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, message.conversation_id
        )
        if not participant:
            return None

        # Check if reactions are allowed
        conversation = crud_conversation.get(session, message.conversation_id)
        if not conversation or not conversation.allow_reactions:
            return None

        return crud_message.add_reaction(session, message_id, emoji, user_id)

    @staticmethod
    def remove_reaction(
        session: Session, message_id: UUID, user_id: UUID, emoji: str
    ) -> Optional[Message]:
        """Remove reaction from a message"""
        message = crud_message.get(session, message_id)
        if not message:
            return None

        return crud_message.remove_reaction(session, message_id, emoji, user_id)

    @staticmethod
    def search_messages(
        session: Session,
        conversation_id: UUID,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Message]:
        """Search messages in a conversation"""
        # Check if user is participant
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return []

        return crud_message.search_messages(
            session, query, conversation_id=conversation_id, limit=limit
        )

    @staticmethod
    def get_unread_count(session: Session, conversation_id: UUID, user_id: UUID) -> int:
        """Get unread message count for user in conversation"""
        # Check if user is participant
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, conversation_id
        )
        if not participant:
            return 0

        unread_messages = crud_message.get_unread_messages(
            session, conversation_id, user_id
        )
        return len(unread_messages)

    @staticmethod
    def get_message_reactions(session: Session, message_id: UUID) -> dict:
        """Get reactions for a message"""
        message = crud_message.get(session, message_id)
        if not message:
            return {}

        # Return reactions data
        reactions = {}
        for reaction in message.reactions:
            emoji = reaction.get("emoji")
            users = reaction.get("users", [])
            reactions[emoji] = {"count": len(users), "users": users}
        return reactions

    @staticmethod
    def forward_message(
        session: Session, message_id: UUID, target_conversation_id: UUID, user_id: UUID
    ) -> Optional[Message]:
        """Forward a message to another conversation"""
        # Get original message
        original_message = crud_message.get(session, message_id)
        if not original_message:
            return None

        # Check if user can access original conversation
        participant = crud_participant.get_by_user_and_conversation(
            session, user_id, original_message.conversation_id
        )
        if not participant:
            return None

        # Check if user can send to target conversation
        target_participant = crud_participant.get_by_user_and_conversation(
            session, user_id, target_conversation_id
        )
        if not target_participant or not target_participant.can_send_messages:
            return None

        # Create forwarded message
        forward_data = MessageCreate(
            conversation_id=target_conversation_id,
            content=f"Forwarded: {original_message.content}",
            type=original_message.type,
            media_url=original_message.media_url,
            forwarded_from=original_message.conversation_id,
        )

        return MessageService.send_message(session, user_id, forward_data)

    @staticmethod
    def schedule_message(
        session: Session,
        sender_id: UUID,
        message_data: MessageCreate,
        scheduled_at: datetime,
    ) -> Optional[Message]:
        """Schedule a message to be sent later"""
        # Check if scheduled time is in future
        if scheduled_at <= datetime.utcnow():
            return None

        # Check permissions
        participant = crud_participant.get_by_user_and_conversation(
            session, sender_id, message_data.conversation_id
        )
        if not participant or not participant.can_send_messages:
            return None

        # Create message with scheduled status
        message_dict = message_data.model_dump()
        message_dict["sender_id"] = sender_id
        message_dict["scheduled_at"] = scheduled_at

        message_create = MessageCreate(**message_dict)
        return crud_message.create(session, obj_in=message_create)


message_service = MessageService()
