import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.stories.model.story import Story
    from app.modules.users.model.user import User


class StoryViewer(SQLModel, table=True):
    """Tracks who has viewed a story"""

    __tablename__ = "story_viewers"

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    story_id: uuid.UUID = Field(foreign_key="stories.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # View metadata
    viewed_at: datetime = Field(default_factory=datetime.utcnow)
    view_duration: Optional[int] = Field(default=None)  # seconds watched
    device_type: Optional[str] = Field(
        default=None, max_length=50
    )  # mobile, desktop, etc.
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv4/IPv6

    # Relationships
    story: "Story" = Relationship(back_populates="viewers")
    user: "User" = Relationship()
