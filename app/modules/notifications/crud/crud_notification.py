from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.notifications.model.notification import (
    Notification,
    NotificationStatus,
)
from app.modules.notifications.schema.notification import (
    NotificationCreate,
    NotificationUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    """CRUD operations for notifications"""

    def get_multi_by_recipient(
        self, session: Session, *, recipient_id: str, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications for a specific recipient"""
        return list(
            session.exec(
                select(Notification)
                .where(Notification.recipient_id == recipient_id)
                .offset(skip)
                .limit(limit)
            )
        )

    def get_unread_by_recipient(
        self, session: Session, *, recipient_id: str
    ) -> List[Notification]:
        """Get unread notifications for a specific recipient"""
        return list(
            session.exec(
                select(Notification).where(
                    Notification.recipient_id == recipient_id,
                    Notification.read_at == None,
                )
            )
        )

    def get_by_sender(
        self, session: Session, *, sender_id: str, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications sent by a specific user"""
        return list(
            session.exec(
                select(Notification)
                .where(Notification.sender_id == sender_id)
                .offset(skip)
                .limit(limit)
            )
        )

    def mark_as_read(
        self, session: Session, *, notification_id: UUID, user_id: str
    ) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = self.get(session=session, id=notification_id)
        if notification and notification.recipient_id == user_id:
            notification.read_at = datetime.utcnow()
            session.add(notification)
            session.commit()
            session.refresh(notification)
            return notification
        return None

    def mark_all_as_read(self, session: Session, *, recipient_id: str) -> int:
        """Mark all notifications as read for a recipient"""
        result = session.exec(
            select(Notification).where(
                Notification.recipient_id == recipient_id, Notification.read_at == None
            )
        )
        notifications = result.all()
        updated_count = len(notifications)

        for notification in notifications:
            notification.read_at = datetime.utcnow()
            session.add(notification)

        session.commit()
        return updated_count

    def get_pending_notifications(
        self, session: Session, *, limit: int = 100
    ) -> List[Notification]:
        """Get notifications pending to be sent"""
        return list(
            session.exec(
                select(Notification)
                .where(Notification.status == NotificationStatus.pending)
                .limit(limit)
            )
        )

    def update_status(
        self, session: Session, *, notification_id: UUID, status: NotificationStatus
    ) -> Optional[Notification]:
        """Update notification status"""
        notification = self.get(session=session, id=notification_id)
        if notification:
            notification.status = status
            notification.updated_at = datetime.utcnow()
            session.add(notification)
            session.commit()
            session.refresh(notification)
            return notification
        return None

    def delete_old_read_notifications(
        self, session: Session, *, days_old: int = 30
    ) -> int:
        """Delete read notifications older than specified days"""
        # TODO: Implement with proper SQLAlchemy syntax
        return 0


crud_notification = CRUDNotification(Notification)
