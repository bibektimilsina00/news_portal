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
    reporter: Optional["User"] = Relationship(
        back_populates="reports_made",
        sa_relationship_kwargs={"foreign_keys": "[ContentReport.reporter_id]"},
    )
    reviewer: Optional["User"] = Relationship(
        back_populates="reports_reviewed",
        sa_relationship_kwargs={"foreign_keys": "[ContentReport.reviewed_by]"},
    )


class ModerationAction(SQLModel, table=True):
    """Moderation actions taken on content."""

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

    id: UUID = Field(default_factory=UUID, primary_key=True)
    action_id: UUID = Field(foreign_key="moderationaction.id", index=True)
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
    appellant: Optional["User"] = Relationship(
        back_populates="moderation_appeals",
        sa_relationship_kwargs={"foreign_keys": "[ModerationAppeal.appellant_id]"},
    )
    reviewer: Optional["User"] = Relationship(
        back_populates="appeal_reviews",
        sa_relationship_kwargs={"foreign_keys": "[ModerationAppeal.reviewed_by]"},
    )


class ContentFlag(SQLModel, table=True):
    """Automated content flags from AI detection."""

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
    user: Optional["User"] = Relationship(
        back_populates="strikes",
        sa_relationship_kwargs={"foreign_keys": "[UserStrike.user_id]"},
    )
    issuer: Optional["User"] = Relationship(
        back_populates="issued_strikes",
        sa_relationship_kwargs={"foreign_keys": "[UserStrike.issued_by]"},
    )


class UserBan(SQLModel, table=True):
    """User bans for severe violations."""

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
    user: Optional["User"] = Relationship(
        back_populates="bans",
        sa_relationship_kwargs={"foreign_keys": "[UserBan.user_id]"},
    )
    banner: Optional["User"] = Relationship(
        back_populates="banned_users",
        sa_relationship_kwargs={"foreign_keys": "[UserBan.banned_by]"},
    )
    appeals: List["BanAppeal"] = Relationship(back_populates="ban")


class BanAppeal(SQLModel, table=True):
    """Appeals against user bans."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    ban_id: UUID = Field(foreign_key="userban.id", index=True)
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
    appellant: Optional["User"] = Relationship(
        back_populates="ban_appeals",
        sa_relationship_kwargs={"foreign_keys": "[BanAppeal.appellant_id]"},
    )
    reviewer: Optional["User"] = Relationship(
        back_populates="ban_appeal_reviews",
        sa_relationship_kwargs={"foreign_keys": "[BanAppeal.reviewed_by]"},
    )


class ModerationRule(SQLModel, table=True):
    """Community guidelines and moderation rules."""

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
