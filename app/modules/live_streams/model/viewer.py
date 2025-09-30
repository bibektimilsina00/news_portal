import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel

from app.shared.enums import ViewerRole

if TYPE_CHECKING:
    pass


class StreamViewer(SQLModel, table=True):
    """Stream viewer model for tracking who watches streams"""

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    stream_id: uuid.UUID = Field(foreign_key="stream.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Viewer info
    role: ViewerRole = Field(default=ViewerRole.viewer)
    is_muted: bool = Field(default=False)
    is_banned: bool = Field(default=False)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = Field(default=None)

    # Engagement tracking
    comments_count: int = Field(default=0, ge=0)
    reactions_count: int = Field(default=0, ge=0)
    badges_sent: int = Field(default=0, ge=0)
    donations_amount: float = Field(default=0.0, ge=0)

    # Session info
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    country: Optional[str] = Field(default=None, max_length=2)
    city: Optional[str] = Field(default=None, max_length=100)

    # Relationships
    # stream: "Stream" = Relationship(back_populates="viewers")
    # user: "User" = Relationship(back_populates="stream_views")

    # Computed properties
    @property
    def is_active(self) -> bool:
        """Check if viewer is currently active"""
        return self.left_at is None

    @property
    def session_duration(self) -> Optional[int]:
        """Get session duration in seconds"""
        if not self.left_at:
            return None
        return int((self.left_at - self.joined_at).total_seconds())

    @property
    def total_engagement(self) -> int:
        """Calculate total engagement score"""
        return self.comments_count + self.reactions_count + (self.badges_sent * 2)
