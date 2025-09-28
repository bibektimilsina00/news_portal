import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import and_
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.news.model.news import News
    from app.modules.posts.model.post import Post
    from app.modules.reels.model.reel import Reel
    from app.modules.users.model.user import User


class CommentBase(SQLModel):
    content: str = Field(max_length=1000)
    is_edited: bool = Field(default=False)
    edited_at: Optional[datetime] = Field(default=None)
    parent_comment_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="comment.id"
    )
    content_type: str = Field(max_length=50)  # post, news, reel, story, etc.
    content_id: uuid.UUID  # ID of the content being commented on


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign keys
    author_id: uuid.UUID = Field(foreign_key="user.id")

    # Relationships
    author: "User" = Relationship(back_populates="comments")
    replies: List["Comment"] = Relationship(
        back_populates="parent_comment",
        sa_relationship_kwargs={"foreign_keys": "[Comment.parent_comment_id]"},
    )
    parent_comment: Optional["Comment"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={
            "foreign_keys": "[Comment.parent_comment_id]",
            "remote_side": "[Comment.id]",
        },
    )

    # Note: Polymorphic relationships to different content types are handled
    # dynamically in the service layer rather than through SQLAlchemy relationships
    # to avoid complex primaryjoin expressions and circular imports


class CommentPublic(CommentBase):
    id: uuid.UUID
    created_at: datetime
    author_id: uuid.UUID
    reply_count: int = 0


class CommentCreate(CommentBase):
    pass


class CommentUpdate(SQLModel):
    content: Optional[str] = Field(default=None, max_length=1000)
