import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel

from app.shared.enums import BadgeType

if TYPE_CHECKING:
    pass


class StreamBadge(SQLModel, table=True):
    """Stream badges/tips model"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    stream_id: uuid.UUID = Field(foreign_key="stream.id", index=True)
    sender_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    recipient_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")

    # Badge details
    badge_type: BadgeType = Field(
        sa_column_kwargs={"server_default": "heart"}
    )  # e.g., "heart", "star", "diamond"
    badge_name: str = Field(max_length=100)
    message: Optional[str] = Field(default=None, max_length=500)

    # Monetary value
    amount: float = Field(ge=0)
    currency: str = Field(default="USD", max_length=3)

    # Animation/visual
    animation_url: Optional[str] = Field(default=None, max_length=1000)
    sound_effect: Optional[str] = Field(default=None, max_length=1000)

    # Timestamps
    sent_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    # stream: "Stream" = Relationship(back_populates="badges")
    # sender: "User" = Relationship()
    # recipient: "User" = Relationship()

    # Computed properties
    @property
    def is_donation(self) -> bool:
        """Check if this is a monetary donation"""
        return self.amount > 0

    @property
    def display_amount(self) -> str:
        """Format amount for display"""
        return ".2f"
