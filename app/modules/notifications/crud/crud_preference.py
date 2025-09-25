from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.notifications.model.preference import NotificationPreference
from app.modules.notifications.schema.preference import (
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDNotificationPreference(
    CRUDBase[
        NotificationPreference,
        NotificationPreferenceCreate,
        NotificationPreferenceUpdate,
    ]
):
    """CRUD operations for notification preferences"""

    def get_by_user(
        self, session: Session, *, user_id: str
    ) -> Optional[NotificationPreference]:
        """Get notification preferences for a specific user"""
        return session.exec(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        ).first()

    def create_or_update(
        self, session: Session, *, user_id: str, obj_in: NotificationPreferenceUpdate
    ) -> NotificationPreference:
        """Create or update notification preferences for a user"""
        # Try to get existing preferences
        existing = self.get_by_user(session=session, user_id=user_id)

        if existing:
            # Update existing
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing, field, value)
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing
        else:
            # Create new
            create_data = obj_in.model_dump()
            create_data["user_id"] = user_id
            db_obj = NotificationPreference(**create_data)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj

    def reset_to_defaults(
        self, session: Session, *, user_id: str
    ) -> Optional[NotificationPreference]:
        """Reset notification preferences to defaults for a user"""
        existing = self.get_by_user(session=session, user_id=user_id)
        if existing:
            # Reset to default values
            existing.email_notifications = True
            existing.push_notifications = True
            existing.sms_notifications = False
            existing.like_notifications = True
            existing.comment_notifications = True
            existing.follow_notifications = True
            existing.mention_notifications = True
            existing.share_notifications = True
            existing.message_notifications = True
            existing.news_notifications = True
            existing.story_notifications = True
            existing.reel_notifications = True
            existing.live_stream_notifications = True
            existing.digest_frequency = "immediate"
            existing.quiet_hours_start = None
            existing.quiet_hours_end = None
            existing.priority_threshold = "medium"
            existing.group_similar = True
            existing.show_preview = True

            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing
        return None


crud_notification_preference = CRUDNotificationPreference(NotificationPreference)
