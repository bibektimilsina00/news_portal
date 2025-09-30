import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class StoryHighlight(SQLModel, table=True):
    """Story highlights - curated collections of stories"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Highlight details
    title: str = Field(max_length=100)
    cover_image_url: Optional[str] = Field(default=None, max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)

    # Settings
    is_private: bool = Field(default=False)
    is_archived: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="story_highlights")
