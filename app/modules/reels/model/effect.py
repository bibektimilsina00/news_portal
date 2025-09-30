import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.shared.enums import EffectCategory, EffectType

if TYPE_CHECKING:
    pass


class Effect(SQLModel, table=True):
    """Video effects for reels"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Effect metadata
    name: str = Field(max_length=100, index=True)
    type: EffectType = Field()
    category: EffectCategory = Field()
    description: Optional[str] = Field(default=None, max_length=500)

    # Effect configuration
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))
    preview_url: Optional[str] = Field(default=None, max_length=1000)

    # Usage tracking
    use_count: int = Field(default=0, ge=0)
    is_premium: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    # reels: List["Reel"] = Relationship(back_populates="applied_effects", link_model=ReelEffect)

    # Computed properties
    @property
    def is_popular(self) -> bool:
        """Check if effect is popular based on usage"""
        return self.use_count > 1000


# class ReelEffect(SQLModel, table=True):
#     """Many-to-many relationship between reels and effects"""


#     reel_id: uuid.UUID = Field(foreign_key="reel.id", primary_key=True)
#     effect_id: uuid.UUID = Field(foreign_key="reel_effects.id", primary_key=True)

#     # Effect application settings
#     start_time: float = Field(default=0.0, ge=0)  # When effect starts in video
#     duration: Optional[float] = Field(default=None, gt=0)  # How long effect lasts
#     intensity: float = Field(default=1.0, ge=0, le=2)  # Effect intensity multiplier

#     # Timestamps
#     applied_at: datetime = Field(default_factory=datetime.utcnow)
