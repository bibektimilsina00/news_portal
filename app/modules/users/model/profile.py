import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class Profile(SQLModel, table=True):
    """Extended user profile information"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)

    # Extended profile information
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

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="profile")
    views: List["ProfileView"] = Relationship(
        back_populates="profile", cascade_delete=True
    )

    class Config:
        from_attributes = True


class ProfileView(SQLModel, table=True):
    """Profile view tracking for analytics"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    profile_id: uuid.UUID = Field(foreign_key="profile.id", index=True)
    viewer_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", index=True
    )
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    viewed_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    profile: "Profile" = Relationship(back_populates="views")
    viewer: Optional["User"] = Relationship(back_populates="profile_views")


class CloseFriend(SQLModel, table=True):
    """Close friends relationships"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    friend_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    added_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[CloseFriend.user_id]"}
    )
    friend: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[CloseFriend.friend_id]"}
    )


class UserBlock(SQLModel, table=True):
    """User blocking relationships"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    blocker_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    blocked_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    reason: Optional[str] = Field(default=None, max_length=500)
    blocked_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    blocker: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UserBlock.blocker_id]"}
    )
    blocked: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UserBlock.blocked_id]"}
    )
