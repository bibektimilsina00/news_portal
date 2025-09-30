import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import ConfigDict
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.news.model.news import News


class Category(SQLModel, table=True):
    """News categories"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(max_length=100, unique=True, index=True)
    slug: str = Field(max_length=100, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    color_hex: Optional[str] = Field(default=None, max_length=7)
    icon_url: Optional[str] = Field(default=None, max_length=500)

    # Hierarchy
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="category.id")
    sort_order: int = Field(default=0)

    # SEO
    meta_title: Optional[str] = Field(default=None, max_length=255)
    meta_description: Optional[str] = Field(default=None, max_length=500)

    # Status
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)

    # Metrics
    news_count: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    news: List["News"] = Relationship(back_populates="category")
    children: List["Category"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "[Category.parent_id]"},
    )
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "foreign_keys": "[Category.parent_id]",
            "remote_side": "[Category.id]",
        },
    )

    model_config = ConfigDict(from_attributes=True)  # type: ignore

    def increment_news_count(self) -> None:
        """Increment news count"""
        self.news_count += 1

    def decrement_news_count(self) -> None:
        """Decrement news count"""
        if self.news_count > 0:
            self.news_count -= 1


class CategoryFollow(SQLModel, table=True):
    """Users following categories"""

    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    category_id: uuid.UUID = Field(foreign_key="category.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)  # type: ignore
