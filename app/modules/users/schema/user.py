import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, EmailStr, field_validator
from sqlmodel import Field, SQLModel

from app.shared.enums.account_type import AccountType
from app.shared.enums.gender import Gender


# Base Schema
class UserBase(SQLModel):
    """Base user schema with common properties"""

    email: EmailStr = Field(unique=True, index=True, max_length=100)
    username: str = Field(unique=True, index=True, max_length=50)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)

    # Profile fields
    full_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    profile_image_url: Optional[str] = Field(default=None, max_length=255)
    website_url: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=100)

    # Account settings
    account_type: AccountType = Field(default=AccountType.personal)
    is_private: bool = Field(default=False)
    is_professional_account: bool = Field(default=False)
    category: Optional[str] = Field(default=None, max_length=50)

    # User type flags
    is_journalist: bool = Field(default=False)
    is_organization: bool = Field(default=False)

    model_config=ConfigDict(use_enum_values=True)



# Creation Schemas
class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str = Field(min_length=8, max_length=40)
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None

    @field_validator("username")
    def validate_username(cls, v):
        if not v.isalnum() and "_" not in v:
            raise ValueError(
                "Username must contain only alphanumeric characters and underscores"
            )
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v.lower()

    @field_validator("password")
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserRegister(SQLModel):
    """Schema for user registration (simplified)"""

    email: EmailStr = Field(max_length=100)
    username: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=100)

    @field_validator("username")
    def validate_username(cls, v):
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "Username must contain only alphanumeric characters and underscores"
            )
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v.lower()


# Update Schemas
class UserUpdate(UserBase):
    """Schema for updating user information"""

    email: Optional[EmailStr] = Field(default=None, max_length=100)
    username: Optional[str] = Field(default=None, max_length=50)
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None

    @field_validator("username")
    def validate_username(cls, v):
        if v is not None:
            if not v.replace("_", "").isalnum():
                raise ValueError(
                    "Username must contain only alphanumeric characters and underscores"
                )
            if len(v) < 3:
                raise ValueError("Username must be at least 3 characters long")
        return v


class UserUpdateMe(SQLModel):
    """Schema for users to update their own profile"""

    full_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    profile_image_url: Optional[str] = Field(default=None, max_length=255)
    website_url: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    account_type: Optional[AccountType] = None
    is_private: Optional[bool] = None
    is_professional_account: Optional[bool] = None
    category: Optional[str] = Field(default=None, max_length=50)

    


# Password Update Schema
class UpdatePassword(SQLModel):
    """Schema for password updates"""

    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

    @field_validator("new_password")
    def validate_new_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError("New password must contain at least one digit")
        if not any(char.isalpha() for char in v):
            raise ValueError("New password must contain at least one letter")
        return v


# Response Schemas
class UserPublic(UserBase):
    """Schema for public user information"""

    id: uuid.UUID
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    last_active: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # type: ignore


class UserProfilePublic(UserPublic):
    """Extended schema for user profile page"""

    is_following: Optional[bool] = None  # For current user's perspective
    mutual_followers_count: Optional[int] = None


class UserPrivate(UserPublic):
    """Schema for user's own profile (includes private fields)"""

    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    email: EmailStr
    is_journalist: bool
    is_organization: bool


class UserList(SQLModel):
    """Schema for paginated user list"""

    users: List[UserPublic]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class UsersPublic(SQLModel):
    """Schema for public users list response"""

    data: List[UserPublic]
    count: int


class UserSearch(SQLModel):
    """Schema for user search results"""

    query: str
    users: List[UserPublic]
    total: int


class UserStats(SQLModel):
    """Schema for user statistics"""

    user_id: uuid.UUID
    follower_count: int
    following_count: int
    post_count: int
    story_count: int
    reel_count: int
    total_likes_received: int
    total_comments_received: int
    engagement_rate: float


# Verification Schemas
class VerificationRequest(SQLModel):
    """Schema for account verification requests"""

    full_name: str = Field(max_length=255)
    category: str = Field(max_length=100)
    identification_document_url: str = Field(max_length=500)
    articles_of_incorporation_url: Optional[str] = Field(default=None, max_length=500)
    official_website_url: Optional[str] = Field(default=None, max_length=255)
    social_media_links: Optional[List[str]] = None


class VerificationResponse(SQLModel):
    """Schema for verification request response"""

    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
