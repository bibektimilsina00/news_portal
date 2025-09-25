import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from sqlmodel import SQLModel


# Base Schemas
class MusicBase(SQLModel):
    """Base music schema"""

    title: str = Field(min_length=1, max_length=200)
    artist: str = Field(min_length=1, max_length=200)
    album: Optional[str] = Field(default=None, max_length=200)
    genre: Optional[str] = Field(default=None, max_length=100)

    # Audio details
    audio_url: str = Field(min_length=1, max_length=1000)
    duration: float = Field(gt=0)
    file_size: int = Field(gt=0)

    # Licensing
    is_licensed: bool = Field(default=True)
    license_type: Optional[str] = Field(default=None, max_length=100)
    attribution_required: bool = Field(default=False)


class MusicCreate(MusicBase):
    """Schema for creating new music"""

    pass


class MusicUpdate(SQLModel):
    """Schema for updating music"""

    title: Optional[str] = Field(default=None, max_length=200)
    artist: Optional[str] = Field(default=None, max_length=200)
    album: Optional[str] = Field(default=None, max_length=200)
    genre: Optional[str] = Field(default=None, max_length=100)
    is_licensed: Optional[bool] = Field(default=None)
    license_type: Optional[str] = Field(default=None, max_length=100)
    attribution_required: Optional[bool] = Field(default=None)


class MusicPublic(MusicBase):
    """Public music schema"""

    id: uuid.UUID
    use_count: int
    trending_score: float
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_trending: bool
    formatted_duration: str


class MusicList(SQLModel):
    """Schema for music list response"""

    data: List[MusicPublic]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class MusicTrending(SQLModel):
    """Schema for trending music"""

    music: MusicPublic
    trending_score: float
    rank: int


class MusicSearch(SQLModel):
    """Schema for music search"""

    query: str = Field(min_length=1, max_length=100)
    genre: Optional[str] = Field(default=None, max_length=100)
    artist: Optional[str] = Field(default=None, max_length=200)
    limit: int = Field(default=20, ge=1, le=100)
