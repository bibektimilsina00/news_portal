import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class NotificationPreferenceBase(SQLModel):
    """Base notification preference model"""

    # General preferences
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=True)
    sms_notifications: bool = Field(default=False)

    # Notification type preferences
    like_notifications: bool = Field(default=True)
    comment_notifications: bool = Field(default=True)
    follow_notifications: bool = Field(default=True)
    mention_notifications: bool = Field(default=True)
    share_notifications: bool = Field(default=True)
    message_notifications: bool = Field(default=True)

    # Content type preferences
    news_notifications: bool = Field(default=True)
    story_notifications: bool = Field(default=True)
    reel_notifications: bool = Field(default=True)
    live_stream_notifications: bool = Field(default=True)

    # Frequency settings
    digest_frequency: str = Field(
        default="immediate", max_length=20
    )  # "immediate", "daily", "weekly"
    quiet_hours_start: Optional[str] = Field(
        default=None, max_length=5
    )  # "22:00" format
    quiet_hours_end: Optional[str] = Field(default=None, max_length=5)  # "08:00" format

    # Advanced preferences
    priority_threshold: str = Field(
        default="medium", max_length=20
    )  # "low", "medium", "high", "urgent"
    group_similar: bool = Field(default=True)  # Group similar notifications
    show_preview: bool = Field(default=True)  # Show message preview in notifications


class NotificationPreference(NotificationPreferenceBase, table=True):
    """Notification preference database model"""

    __tablename__ = "notification_preferences"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )

    # Foreign key
    user_id: str = Field(foreign_key="user.id", unique=True, index=True)

    # Relationship
    user: "User" = Relationship(back_populates="notification_preferences")

    # Custom preferences as JSON (for extensibility)
    custom_preferences: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Methods for checking preferences
    def should_send_notification(
        self, notification_type: str, priority: str = "medium"
    ) -> bool:
        """Check if notification should be sent based on preferences"""
        # Check if notifications are enabled
        if not self.push_notifications:
            return False

        # Check priority threshold
        priority_levels = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
        threshold_level = priority_levels.get(self.priority_threshold, 2)
        notification_level = priority_levels.get(priority, 2)

        if notification_level < threshold_level:
            return False

        # Check type-specific preferences
        type_preferences = {
            "like": self.like_notifications,
            "comment": self.comment_notifications,
            "follow": self.follow_notifications,
            "mention": self.mention_notifications,
            "share": self.share_notifications,
            "message": self.message_notifications,
            "news_published": self.news_notifications,
            "story_added": self.story_notifications,
            "reel_published": self.reel_notifications,
            "live_stream_started": self.live_stream_notifications,
        }

        return type_preferences.get(notification_type, True)

    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False

        from datetime import datetime

        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if self.quiet_hours_start > self.quiet_hours_end:
            return (
                current_time >= self.quiet_hours_start
                or current_time <= self.quiet_hours_end
            )
        else:
            return self.quiet_hours_start <= current_time <= self.quiet_hours_end
