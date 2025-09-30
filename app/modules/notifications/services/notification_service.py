from typing import List, Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.notifications.crud.crud_notification import crud_notification
from app.modules.notifications.crud.crud_preference import crud_notification_preference
from app.modules.notifications.model.notification import (
    Notification,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from app.modules.notifications.schema.notification import (
    NotificationCreate,
)


class NotificationService:
    """Service layer for notification operations"""

    @staticmethod
    def create_notification(
        session: Session,
        recipient_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        sender_id: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.medium,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata_: Optional[dict] = None,
    ) -> Notification:
        """Create a new notification"""
        notification_in = NotificationCreate(
            recipient_id=recipient_id,
            sender_id=sender_id,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            entity_type=entity_type,
            entity_id=entity_id,
            action_url=action_url,
            metadata_=metadata_,
        )
        return crud_notification.create(session=session, obj_in=notification_in)

    @staticmethod
    def get_user_notifications(
        session: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        include_read: bool = True,
    ) -> List[Notification]:
        """Get notifications for a user"""
        if include_read:
            return crud_notification.get_multi_by_recipient(
                session=session, recipient_id=user_id, skip=skip, limit=limit
            )
        else:
            return crud_notification.get_unread_by_recipient(
                session=session, recipient_id=user_id
            )

    @staticmethod
    def get_unread_count(session: Session, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        unread = crud_notification.get_unread_by_recipient(
            session=session, recipient_id=user_id
        )
        return len(unread)

    @staticmethod
    def mark_as_read(
        session: Session, notification_id: UUID, user_id: str
    ) -> Optional[Notification]:
        """Mark a notification as read"""
        return crud_notification.mark_as_read(
            session=session, notification_id=notification_id, user_id=user_id
        )

    @staticmethod
    def mark_all_as_read(session: Session, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        return crud_notification.mark_all_as_read(session=session, recipient_id=user_id)

    @staticmethod
    def create_like_notification(
        session: Session,
        recipient_id: str,
        sender_id: str,
        entity_type: str,
        entity_id: str,
        entity_title: Optional[str] = None,
    ) -> Notification:
        """Create a like notification"""
        title = "Someone liked your post"
        if entity_title:
            title = f"Someone liked your post: {entity_title}"

        return NotificationService.create_notification(
            session=session,
            recipient_id=recipient_id,
            sender_id=sender_id,
            notification_type=NotificationType.LIKE,
            title=title,
            message="Your post received a like",
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @staticmethod
    def create_comment_notification(
        session: Session,
        recipient_id: str,
        sender_id: str,
        entity_type: str,
        entity_id: str,
        comment_text: str,
        entity_title: Optional[str] = None,
    ) -> Notification:
        """Create a comment notification"""
        title = "Someone commented on your post"
        if entity_title:
            title = f"Someone commented on: {entity_title}"

        # Truncate comment text for notification
        message = (
            comment_text[:100] + "..." if len(comment_text) > 100 else comment_text
        )

        return NotificationService.create_notification(
            session=session,
            recipient_id=recipient_id,
            sender_id=sender_id,
            notification_type=NotificationType.COMMENT,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @staticmethod
    def create_follow_notification(
        session: Session, recipient_id: str, sender_id: str
    ) -> Notification:
        """Create a follow notification"""
        return NotificationService.create_notification(
            session=session,
            recipient_id=recipient_id,
            sender_id=sender_id,
            notification_type=NotificationType.FOLLOW,
            title="New follower",
            message="Someone started following you",
            entity_type="user",
            entity_id=sender_id,
        )

    @staticmethod
    def create_mention_notification(
        session: Session,
        recipient_id: str,
        sender_id: str,
        entity_type: str,
        entity_id: str,
        mention_text: str,
    ) -> Notification:
        """Create a mention notification"""
        return NotificationService.create_notification(
            session=session,
            recipient_id=recipient_id,
            sender_id=sender_id,
            notification_type=NotificationType.MENTION,
            title="You were mentioned",
            message=f"You were mentioned in: {mention_text[:100]}...",
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @staticmethod
    def should_send_notification(
        session: Session, user_id: str, notification_type: NotificationType
    ) -> bool:
        """Check if notification should be sent based on user preferences"""
        preferences = crud_notification_preference.get_by_user(
            session=session, user_id=user_id
        )
        if not preferences:
            return True  # Default to sending if no preferences set

        return preferences.should_send_notification(notification_type.value)

    @staticmethod
    def get_pending_notifications(
        session: Session, limit: int = 100
    ) -> List[Notification]:
        """Get notifications pending to be sent (for background processing)"""
        return crud_notification.get_pending_notifications(session=session, limit=limit)

    @staticmethod
    def update_notification_status(
        session: Session, notification_id: UUID, status: NotificationStatus
    ) -> Optional[Notification]:
        """Update notification delivery status"""
        return crud_notification.update_status(
            session=session, notification_id=notification_id, status=status
        )


notification_service = NotificationService()
