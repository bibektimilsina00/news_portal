import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class SearchHistory(SQLModel, table=True):
    """Search history model for user search tracking"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # User who performed the search
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Search details
    query: str = Field(max_length=500, index=True)
    search_type: str = Field(
        max_length=50, default="general"
    )  # "general", "user", "hashtag", etc.
    result_count: int = Field(default=0, ge=0)

    # Search filters used
    filters: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Timestamps
    searched_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="search_history")
