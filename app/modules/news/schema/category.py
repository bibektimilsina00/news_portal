import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel


# Base Schemas
class CategoryBase(SQLModel):
    """Base category schema"""

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    color_hex: Optional[str] = Field(default=None, max_length=7)
    icon_url: Optional[str] = Field(default=None, max_length=500)

    # Hierarchy
    parent_id: Optional[uuid.UUID] = Field(default=None)
    sort_order: int = Field(default=0, ge=0)

    # SEO
    meta_title: Optional[str] = Field(default=None, max_length=255)
    meta_description: Optional[str] = Field(default=None, max_length=500)

    # Status
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)


# Public Schemas
class CategoryPublic(CategoryBase):
    """Public category schema"""

    id: uuid.UUID
    news_count: int
    created_at: datetime
    updated_at: Optional[datetime]


# Create Schemas
class CategoryCreate(CategoryBase):
    """Category creation schema"""

    pass


# Update Schemas
class CategoryUpdate(BaseModel):
    """Category update schema"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    color_hex: Optional[str] = Field(default=None, max_length=7)
    icon_url: Optional[str] = Field(default=None, max_length=500)
    parent_id: Optional[uuid.UUID] = Field(default=None)
    sort_order: Optional[int] = Field(default=None, ge=0)
    meta_title: Optional[str] = Field(default=None, max_length=255)
    meta_description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)
    is_featured: Optional[bool] = Field(default=None)


# Response Schemas
class CategoryWithChildren(CategoryPublic):
    """Category with children hierarchy"""

    children: List["CategoryWithChildren"] = Field(default_factory=list)


CategoryWithChildren.model_rebuild()


class CategoriesList(BaseModel):
    """List of categories response"""

    data: List[CategoryPublic]
    total: int
    page: int = 1
    per_page: int = 50


class CategoryStats(BaseModel):
    """Category statistics"""

    total_categories: int
    active_categories: int
    featured_categories: int
    total_news: int
