import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.posts.model.post import Post
    from app.modules.users.model.user import User


class BookmarkBase(SQLModel):
    pass


class Bookmark(BookmarkBase, table=True):
    """Bookmark model for posts"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Foreign Keys
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="bookmarks")
    post: "Post" = Relationship(back_populates="bookmarks")


class BookmarkPublic(BookmarkBase):
    id: uuid.UUID
    user_id: uuid.UUID
    post_id: uuid.UUID
    created_at: datetime


class BookmarkCreate(BookmarkBase):
    post_id: uuid.UUID
