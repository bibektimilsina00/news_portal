import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field
from sqlmodel import SQLModel

from app.modules.reels.model.effect import EffectCategory, EffectType


# Base Schemas
class EffectBase(SQLModel):
    """Base effect schema"""

    name: str = Field(min_length=1, max_length=100)
    type: EffectType
    category: EffectCategory
    description: Optional[str] = Field(default=None, max_length=500)

    # Effect configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    preview_url: Optional[str] = Field(default=None, max_length=1000)

    # Settings
    is_premium: bool = Field(default=False)


class EffectCreate(EffectBase):
    """Schema for creating new effect"""

    pass


class EffectUpdate(SQLModel):
    """Schema for updating effect"""

    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    config: Optional[Dict[str, Any]] = Field(default=None)
    preview_url: Optional[str] = Field(default=None, max_length=1000)
    is_premium: Optional[bool] = Field(default=None)


class EffectPublic(EffectBase):
    """Public effect schema"""

    id: uuid.UUID
    use_count: int
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_popular: bool


class EffectList(SQLModel):
    """Schema for effect list response"""

    data: List[EffectPublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class EffectCategoryList(SQLModel):
    """Schema for effects grouped by category"""

    category: EffectCategory
    effects: List[EffectPublic]
    total: int


class ReelEffectApply(SQLModel):
    """Schema for applying effect to reel"""

    effect_id: uuid.UUID
    start_time: float = Field(default=0.0, ge=0)
    duration: Optional[float] = Field(default=None, gt=0)
    intensity: float = Field(default=1.0, ge=0, le=2)


class ReelEffectUpdate(SQLModel):
    """Schema for updating applied effect"""

    start_time: Optional[float] = Field(default=None, ge=0)
    duration: Optional[float] = Field(default=None, gt=0)
    intensity: Optional[float] = Field(default=None, ge=0, le=2)
