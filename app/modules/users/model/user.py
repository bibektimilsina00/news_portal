import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import JSON, Column, Enum, Field, Relationship

from app.modules.users.schema.user import UserBase
from app.shared.enums.account_type import AccountType
from app.shared.enums.gender import Gender

# if TYPE_CHECKING:
# from app.modules.news.model.news import News
# from app.modules.posts.model.post import Post
# from app.modules.reels.model.reel import Reel
# from app.modules.stories.model.story import Story


class User(UserBase, table=True):
    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Authentication Fields
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    # Profile Information
    full_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    profile_image_url: Optional[str] = Field(default=None, max_length=255)
    website_url: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[datetime] = Field(default=None)
    gender: Optional[Gender] = Field(default=None)

    # Account Settings
    account_type: AccountType = Field(default=AccountType.PERSONAL)
    is_private: bool = Field(default=False)
    is_professional_account: bool = Field(default=False)
    category: Optional[str] = Field(
        default=None, max_length=50
    )  # For business accounts

    # User Type Flags
    is_journalist: bool = Field(default=False)
    is_organization: bool = Field(default=False)

    # Social Media Counters
    follower_count: int = Field(default=0)
    following_count: int = Field(default=0)
    post_count: int = Field(default=0)

    # Metadata
    last_active: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    # posts: List["Post"] = Relationship(back_populates="owner", cascade_delete=True)
    # news: List["News"] = Relationship(back_populates="author", cascade_delete=True)
    # stories: List["Story"] = Relationship(back_populates="owner", cascade_delete=True)
    # reels: List["Reel"] = Relationship(back_populates="owner", cascade_delete=True)

    # # Social Relationships (through association tables)
    # followers: List["Follow"] = Relationship(
    #     back_populates="following",
    #     sa_relationship_kwargs={"foreign_keys": "Follow.following_id"},
    # )
    # following: List["Follow"] = Relationship(
    #     back_populates="follower",
    #     sa_relationship_kwargs={"foreign_keys": "Follow.follower_id"},
    # )

    class Config:
        orm_mode = True
        use_enum_values = True

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
