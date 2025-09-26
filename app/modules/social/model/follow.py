import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class Follow(SQLModel, table=True):
    """Follow relationship between users"""


    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    follower_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    following_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    follower: "User" = Relationship(
        back_populates="following",
        sa_relationship_kwargs={"foreign_keys": "Follow.follower_id"},
    )
    following: "User" = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={"foreign_keys": "Follow.following_id"},
    )

    class Config:
        from_attributes = True
