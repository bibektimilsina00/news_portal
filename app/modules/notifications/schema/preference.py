import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class NotificationPreferenceBase(SQLModel):
    """Base notification preference schema"""

    # General preferences
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False

    # Notification type preferences
    like_notifications: bool = True
    comment_notifications: bool = True
    follow_notifications: bool = True
    mention_notifications: bool = True
    share_notifications: bool = True
    message_notifications: bool = True

    # Content type preferences
    news_notifications: bool = True
    story_notifications: bool = True
    reel_notifications: bool = True
    live_stream_notifications: bool = True

    # Frequency settings
    digest_frequency: str = Field(default="immediate", max_length=20)
    quiet_hours_start: Optional[str] = Field(default=None, max_length=5)
    quiet_hours_end: Optional[str] = Field(default=None, max_length=5)

    # Advanced preferences
    priority_threshold: str = Field(default="medium", max_length=20)
    group_similar: bool = True
    show_preview: bool = True


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preferences"""

    user_id: str

    # Custom preferences
    custom_preferences: Optional[dict] = None


class NotificationPreferenceUpdate(SQLModel):
    """Schema for updating notification preferences"""

    # General preferences
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None

    # Notification type preferences
    like_notifications: Optional[bool] = None
    comment_notifications: Optional[bool] = None
    follow_notifications: Optional[bool] = None
    mention_notifications: Optional[bool] = None
    share_notifications: Optional[bool] = None
    message_notifications: Optional[bool] = None

    # Content type preferences
    news_notifications: Optional[bool] = None
    story_notifications: Optional[bool] = None
    reel_notifications: Optional[bool] = None
    live_stream_notifications: Optional[bool] = None

    # Frequency settings
    digest_frequency: Optional[str] = Field(default=None, max_length=20)
    quiet_hours_start: Optional[str] = Field(default=None, max_length=5)
    quiet_hours_end: Optional[str] = Field(default=None, max_length=5)

    # Advanced preferences
    priority_threshold: Optional[str] = Field(default=None, max_length=20)
    group_similar: Optional[bool] = None
    show_preview: Optional[bool] = None

    # Custom preferences
    custom_preferences: Optional[dict] = None


class NotificationPreferencePublic(NotificationPreferenceBase):
    """Public notification preference schema"""

    id: str
    user_id: str

    # Custom preferences
    custom_preferences: Optional[dict] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime


class NotificationPreferenceWithUser(NotificationPreferencePublic):
    """Notification preference with user information"""

    user: "UserPublic"


# Import here to avoid circular imports
from app.modules.users.schema.user import UserPublic
