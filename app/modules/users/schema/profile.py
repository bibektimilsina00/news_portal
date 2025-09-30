import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_validator
from sqlmodel import SQLModel


# Base Profile Schema
class ProfileBase(SQLModel):
    """Base profile schema with common properties"""

    bio: Optional[str] = Field(default=None, max_length=500)
    website_url: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=100)

    # Media
    profile_image_url: Optional[str] = Field(default=None, max_length=500)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)

    # Professional information
    occupation: Optional[str] = Field(default=None, max_length=100)
    company: Optional[str] = Field(default=None, max_length=100)
    education: Optional[str] = Field(default=None, max_length=200)

    # Contact information
    phone_number: Optional[str] = Field(default=None, max_length=20)
    contact_email: Optional[str] = Field(default=None, max_length=100)

    # Social media links
    twitter_url: Optional[str] = Field(default=None, max_length=255)
    facebook_url: Optional[str] = Field(default=None, max_length=255)
    instagram_url: Optional[str] = Field(default=None, max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=255)
    youtube_url: Optional[str] = Field(default=None, max_length=255)

    # Portfolio/Professional links
    portfolio_url: Optional[str] = Field(default=None, max_length=255)
    professional_website: Optional[str] = Field(default=None, max_length=255)

    # Preferences
    is_profile_public: bool = Field(default=True)
    show_email: bool = Field(default=False)
    show_phone: bool = Field(default=False)
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=True)

    @field_validator(
        "website_url",
        "twitter_url",
        "facebook_url",
        "instagram_url",
        "linkedin_url",
        "youtube_url",
        "portfolio_url",
        "professional_website",
    )
    @classmethod
    def validate_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        if v:
            # Basic phone number validation (allow digits, spaces, hyphens, parentheses)
            import re

            if not re.match(r"^[\d\s\-\(\)\+]+$", v):
                raise ValueError("Invalid phone number format")
        return v


# Create/Update Schemas
class ProfileCreate(ProfileBase):
    """Schema for creating a new profile"""

    pass


class ProfileUpdate(ProfileBase):
    """Schema for updating profile information"""

    pass


class ProfileUpdateMe(SQLModel):
    """Schema for users to update their own profile"""

    bio: Optional[str] = Field(default=None, max_length=500)
    website_url: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=100)

    # Media
    profile_image_url: Optional[str] = Field(default=None, max_length=500)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)

    # Professional information
    occupation: Optional[str] = Field(default=None, max_length=100)
    company: Optional[str] = Field(default=None, max_length=100)
    education: Optional[str] = Field(default=None, max_length=200)

    # Contact information
    phone_number: Optional[str] = Field(default=None, max_length=20)
    contact_email: Optional[str] = Field(default=None, max_length=100)

    # Social media links
    twitter_url: Optional[str] = Field(default=None, max_length=255)
    facebook_url: Optional[str] = Field(default=None, max_length=255)
    instagram_url: Optional[str] = Field(default=None, max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=255)
    youtube_url: Optional[str] = Field(default=None, max_length=255)

    # Portfolio/Professional links
    portfolio_url: Optional[str] = Field(default=None, max_length=255)
    professional_website: Optional[str] = Field(default=None, max_length=255)

    # Preferences
    is_profile_public: Optional[bool] = None
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None


# Response Schemas
class ProfilePublic(ProfileBase):
    """Schema for public profile information"""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProfilePrivate(ProfilePublic):
    """Schema for user's own profile (includes private fields)"""

    pass


class ProfileWithStats(ProfilePublic):
    """Profile with additional statistics"""

    total_views: int = 0
    total_followers: int = 0
    total_following: int = 0
    is_following: Optional[bool] = None
    is_close_friend: Optional[bool] = None


# Close Friends Schemas
class CloseFriendBase(SQLModel):
    """Base close friend schema"""

    friend_id: uuid.UUID


class CloseFriendCreate(CloseFriendBase):
    """Schema for adding a close friend"""

    pass


class CloseFriendResponse(SQLModel):
    """Schema for close friend response"""

    id: uuid.UUID
    user_id: uuid.UUID
    friend_id: uuid.UUID
    added_at: datetime

    # Friend details (populated by service)
    friend_username: Optional[str] = None
    friend_full_name: Optional[str] = None
    friend_profile_image: Optional[str] = None


class CloseFriendsList(SQLModel):
    """Schema for close friends list"""

    friends: List[CloseFriendResponse]
    total: int


# User Block Schemas
class UserBlockBase(SQLModel):
    """Base user block schema"""

    blocked_id: uuid.UUID
    reason: Optional[str] = Field(default=None, max_length=500)


class UserBlockCreate(UserBlockBase):
    """Schema for blocking a user"""

    pass


class UserBlockResponse(SQLModel):
    """Schema for user block response"""

    id: uuid.UUID
    blocker_id: uuid.UUID
    blocked_id: uuid.UUID
    reason: Optional[str] = None
    blocked_at: datetime

    # Blocked user details (populated by service)
    blocked_username: Optional[str] = None
    blocked_full_name: Optional[str] = None
    blocked_profile_image: Optional[str] = None


class UserBlocksList(SQLModel):
    """Schema for blocked users list"""

    blocks: List[UserBlockResponse]
    total: int


# Profile Analytics Schemas
class ProfileViewStats(SQLModel):
    """Profile view statistics"""

    total_views: int
    unique_viewers: int
    views_today: int
    views_this_week: int
    views_this_month: int
    top_viewer_locations: List[dict]  # [{"country": "US", "count": 10}, ...]


class ProfileAnalytics(SQLModel):
    """Complete profile analytics"""

    profile_stats: ProfileViewStats
    engagement_rate: float
    follower_growth: List[dict]  # [{"date": "2024-01-01", "followers": 100}, ...]
    content_performance: List[dict]  # Post engagement metrics


# Settings Schemas
class PrivacySettings(SQLModel):
    """Privacy settings for profile"""

    is_profile_public: bool = True
    show_email: bool = False
    show_phone: bool = False
    allow_messages_from: str = Field(
        default="everyone"
    )  # everyone, followers, close_friends


class NotificationSettings(SQLModel):
    """Notification settings"""

    email_notifications: bool = True
    push_notifications: bool = True
    notify_on_follow: bool = True
    notify_on_like: bool = True
    notify_on_comment: bool = True
    notify_on_mention: bool = True
    notify_on_message: bool = True


class ProfileSettings(SQLModel):
    """Complete profile settings"""

    privacy: PrivacySettings
    notifications: NotificationSettings


class ProfileSettingsUpdate(SQLModel):
    """Schema for updating profile settings"""

    privacy: Optional[PrivacySettings] = None
    notifications: Optional[NotificationSettings] = None
