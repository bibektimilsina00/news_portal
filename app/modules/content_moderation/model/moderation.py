from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.news.model.news import News
    from app.modules.posts.model.post import Post
    from app.modules.reels.model.reel import Reel
    from app.modules.stories.model.story import Story
    from app.modules.users.model.user import User


class ContentReport(SQLModel, table=True):
    """User reports for content moderation."""

    __tablename__ = "content_report"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    reporter_id: UUID = Field(foreign_key="user.id", index=True)
    content_type: str = Field(max_length=50)  # post, news, story, reel, comment, etc.
    content_id: UUID = Field(index=True)  # ID of the reported content
    reason: str = Field(max_length=100)  # spam, harassment, hate_speech, etc.
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending")  # pending, reviewed, resolved, dismissed
    severity: str = Field(default="low")  # low, medium, high, critical
    reviewed_by: Optional[UUID] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = None
    resolution: Optional[str] = Field(default=None, max_length=500)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    reporter: Optional["User"] = Relationship(back_populates="reports_made")
    reviewer: Optional["User"] = Relationship(back_populates="reports_reviewed")


class ModerationAction(SQLModel, table=True):
    """Moderation actions taken on content."""

    __tablename__ = "moderation_action"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    moderator_id: UUID = Field(foreign_key="user.id", index=True)
    content_type: str = Field(max_length=50)
    content_id: UUID = Field(index=True)
    action_type: str = Field(max_length=50)  # remove, hide, warn, ban_user, etc.
    reason: str = Field(max_length=500)
    severity: str = Field(default="medium")  # low, medium, high, critical
    duration_hours: Optional[int] = Field(default=None)  # For temporary actions
    appeal_deadline: Optional[datetime] = None
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    moderator: Optional["User"] = Relationship(back_populates="moderation_actions")
    appeals: List["ModerationAppeal"] = Relationship(back_populates="action")


class ModerationAppeal(SQLModel, table=True):
    """Appeals against moderation actions."""

    __tablename__ = "moderation_appeal"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    action_id: UUID = Field(foreign_key="moderation_action.id", index=True)
    appellant_id: UUID = Field(foreign_key="user.id", index=True)
    reason: str = Field(max_length=1000)
    evidence: Optional[str] = Field(default=None, max_length=2000)
    status: str = Field(default="pending")  # pending, approved, denied, under_review
    reviewed_by: Optional[UUID] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = Field(default=None, max_length=1000)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    action: Optional["ModerationAction"] = Relationship(back_populates="appeals")
    appellant: Optional["User"] = Relationship(back_populates="moderation_appeals")
    reviewer: Optional["User"] = Relationship(back_populates="appeal_reviews")


class ContentFlag(SQLModel, table=True):
    """Automated content flags from AI detection."""

    __tablename__ = "content_flag"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    content_type: str = Field(max_length=50)
    content_id: UUID = Field(index=True)
    flag_type: str = Field(
        max_length=50
    )  # spam, hate_speech, copyright, fake_news, etc.
    confidence_score: Decimal = Field(
        max_digits=5, decimal_places=4
    )  # 0.0000 to 1.0000
    detected_text: Optional[str] = Field(default=None, max_length=1000)
    flagged_by: str = Field(max_length=50)  # ai_model_name or system
    status: str = Field(default="active")  # active, resolved, dismissed
    resolved_by: Optional[UUID] = Field(default=None, foreign_key="user.id")
    resolved_at: Optional[datetime] = None
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    resolver: Optional["User"] = Relationship(back_populates="resolved_flags")


class UserStrike(SQLModel, table=True):
    """User strikes for violations."""

    __tablename__ = "user_strike"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    issued_by: UUID = Field(foreign_key="user.id", index=True)
    reason: str = Field(max_length=500)
    severity: str = Field(default="medium")  # warning, minor, major, critical
    strike_count: int = Field(default=1)
    total_strikes: int = Field(default=1)  # Cumulative count
    expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="strikes")
    issuer: Optional["User"] = Relationship(back_populates="issued_strikes")


class UserBan(SQLModel, table=True):
    """User bans for severe violations."""

    __tablename__ = "user_ban"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    banned_by: UUID = Field(foreign_key="user.id", index=True)
    reason: str = Field(max_length=500)
    ban_type: str = Field(default="temporary")  # temporary, permanent
    duration_hours: Optional[int] = Field(default=None)
    expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    appeal_allowed: bool = Field(default=True)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="bans")
    banner: Optional["User"] = Relationship(back_populates="banned_users")
    appeals: List["BanAppeal"] = Relationship(back_populates="ban")


class BanAppeal(SQLModel, table=True):
    """Appeals against user bans."""

    __tablename__ = "ban_appeal"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    ban_id: UUID = Field(foreign_key="user_ban.id", index=True)
    appellant_id: UUID = Field(foreign_key="user.id", index=True)
    reason: str = Field(max_length=1000)
    evidence: Optional[str] = Field(default=None, max_length=2000)
    status: str = Field(default="pending")  # pending, approved, denied, under_review
    reviewed_by: Optional[UUID] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = Field(default=None, max_length=1000)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    ban: Optional["UserBan"] = Relationship(back_populates="appeals")
    appellant: Optional["User"] = Relationship(back_populates="ban_appeals")
    reviewer: Optional["User"] = Relationship(back_populates="ban_appeal_reviews")


class ModerationRule(SQLModel, table=True):
    """Community guidelines and moderation rules."""

    __tablename__ = "moderation_rule"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    title: str = Field(max_length=200)
    description: str
    category: str = Field(max_length=50)  # content, behavior, spam, etc.
    severity: str = Field(default="medium")  # low, medium, high, critical
    is_active: bool = Field(default=True)
    auto_action: Optional[str] = Field(
        default=None, max_length=50
    )  # Action to take automatically
    requires_review: bool = Field(default=True)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class ModerationLog(SQLModel, table=True):
    """Audit log for all moderation activities."""

    __tablename__ = "moderation_log"

    id: UUID = Field(default_factory=UUID, primary_key=True)
    moderator_id: Optional[UUID] = Field(
        default=None, foreign_key="user.id", index=True
    )
    action_type: str = Field(
        max_length=50
    )  # report_reviewed, content_removed, user_banned, etc.
    target_type: str = Field(max_length=50)  # user, post, comment, etc.
    target_id: UUID = Field(index=True)
    description: str = Field(max_length=500)
    old_value: Optional[str] = Field(default=None, max_length=1000)
    new_value: Optional[str] = Field(default=None, max_length=1000)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    moderator: Optional["User"] = Relationship(back_populates="moderation_logs")
