import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.reels.model.reel import Reel


class Music(SQLModel, table=True):
    """Music tracks for reels"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Music metadata
    title: str = Field(max_length=200, index=True)
    artist: str = Field(max_length=200, index=True)
    album: Optional[str] = Field(default=None, max_length=200)
    genre: Optional[str] = Field(default=None, max_length=100)

    # Audio details
    audio_url: str = Field(max_length=1000)
    duration: float = Field(gt=0)  # Duration in seconds
    file_size: int = Field(gt=0)

    # Usage tracking
    use_count: int = Field(default=0, ge=0)
    trending_score: float = Field(default=0.0, ge=0)

    # Licensing and rights
    is_licensed: bool = Field(default=True)
    license_type: Optional[str] = Field(default=None, max_length=100)
    attribution_required: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    reels: List["Reel"] = Relationship(back_populates="music")

    # Computed properties
    @property
    def is_trending(self) -> bool:
        """Check if music is currently trending"""
        return self.trending_score > 100.0

    @property
    def formatted_duration(self) -> str:
        """Format duration as MM:SS"""
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return "02d"
