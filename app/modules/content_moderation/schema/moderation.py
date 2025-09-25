from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import SQLModel


# Content Report Schemas
class ContentReportBase(SQLModel):
    content_type: str = Field(max_length=50)
    content_id: UUID
    reason: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    severity: str = Field(default="low")
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ContentReportCreate(ContentReportBase):
    pass


class ContentReportUpdate(SQLModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    resolution: Optional[str] = Field(default=None, max_length=500)
    extra_data: Optional[Dict[str, Any]] = None


class ContentReport(ContentReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID
    status: str
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContentReportPublic(ContentReportBase):
    id: UUID
    reporter_id: UUID
    status: str
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime


# Moderation Action Schemas
class ModerationActionBase(SQLModel):
    content_type: str = Field(max_length=50)
    content_id: UUID
    action_type: str = Field(max_length=50)
    reason: str = Field(max_length=500)
    severity: str = Field(default="medium")
    duration_hours: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ModerationActionCreate(ModerationActionBase):
    pass


class ModerationActionUpdate(SQLModel):
    action_type: Optional[str] = Field(default=None, max_length=50)
    reason: Optional[str] = Field(default=None, max_length=500)
    severity: Optional[str] = None
    duration_hours: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None


class ModerationAction(ModerationActionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    moderator_id: UUID
    appeal_deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ModerationActionPublic(ModerationActionBase):
    id: UUID
    moderator_id: UUID
    appeal_deadline: Optional[datetime] = None
    created_at: datetime


# Moderation Appeal Schemas
class ModerationAppealBase(SQLModel):
    action_id: UUID
    reason: str = Field(max_length=1000)
    evidence: Optional[str] = Field(default=None, max_length=2000)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ModerationAppealCreate(ModerationAppealBase):
    pass


class ModerationAppealUpdate(SQLModel):
    status: Optional[str] = None
    review_notes: Optional[str] = Field(default=None, max_length=1000)
    extra_data: Optional[Dict[str, Any]] = None


class ModerationAppeal(ModerationAppealBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    appellant_id: UUID
    status: str
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ModerationAppealPublic(ModerationAppealBase):
    id: UUID
    appellant_id: UUID
    status: str
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime


# Content Flag Schemas
class ContentFlagBase(SQLModel):
    content_type: str = Field(max_length=50)
    content_id: UUID
    flag_type: str = Field(max_length=50)
    confidence_score: Decimal = Field(max_digits=5, decimal_places=4)
    detected_text: Optional[str] = Field(default=None, max_length=1000)
    flagged_by: str = Field(max_length=50)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ContentFlagCreate(ContentFlagBase):
    pass


class ContentFlagUpdate(SQLModel):
    status: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class ContentFlag(ContentFlagBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContentFlagPublic(ContentFlagBase):
    id: UUID
    status: str
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime


# User Strike Schemas
class UserStrikeBase(SQLModel):
    user_id: UUID
    reason: str = Field(max_length=500)
    severity: str = Field(default="medium")
    strike_count: int = Field(default=1)
    expires_at: Optional[datetime] = None
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserStrikeCreate(UserStrikeBase):
    pass


class UserStrikeUpdate(SQLModel):
    severity: Optional[str] = None
    strike_count: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class UserStrike(UserStrikeBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    issued_by: UUID
    total_strikes: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserStrikePublic(UserStrikeBase):
    id: UUID
    issued_by: UUID
    total_strikes: int
    is_active: bool
    created_at: datetime


# User Ban Schemas
class UserBanBase(SQLModel):
    user_id: UUID
    reason: str = Field(max_length=500)
    ban_type: str = Field(default="temporary")
    duration_hours: Optional[int] = None
    appeal_allowed: bool = Field(default=True)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserBanCreate(UserBanBase):
    pass


class UserBanUpdate(SQLModel):
    ban_type: Optional[str] = None
    duration_hours: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    appeal_allowed: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class UserBan(UserBanBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    banned_by: UUID
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserBanPublic(UserBanBase):
    id: UUID
    banned_by: UUID
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime


# Ban Appeal Schemas
class BanAppealBase(SQLModel):
    ban_id: UUID
    reason: str = Field(max_length=1000)
    evidence: Optional[str] = Field(default=None, max_length=2000)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BanAppealCreate(BanAppealBase):
    pass


class BanAppealUpdate(SQLModel):
    status: Optional[str] = None
    review_notes: Optional[str] = Field(default=None, max_length=1000)
    extra_data: Optional[Dict[str, Any]] = None


class BanAppeal(BanAppealBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    appellant_id: UUID
    status: str
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class BanAppealPublic(BanAppealBase):
    id: UUID
    appellant_id: UUID
    status: str
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime


# Moderation Rule Schemas
class ModerationRuleBase(SQLModel):
    title: str = Field(max_length=200)
    description: str
    category: str = Field(max_length=50)
    severity: str = Field(default="medium")
    auto_action: Optional[str] = Field(default=None, max_length=50)
    requires_review: bool = Field(default=True)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ModerationRuleCreate(ModerationRuleBase):
    pass


class ModerationRuleUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=50)
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    auto_action: Optional[str] = Field(default=None, max_length=50)
    requires_review: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class ModerationRule(ModerationRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ModerationRulePublic(ModerationRuleBase):
    id: UUID
    is_active: bool
    created_at: datetime


# Moderation Log Schemas
class ModerationLogBase(SQLModel):
    action_type: str = Field(max_length=50)
    target_type: str = Field(max_length=50)
    target_id: UUID
    description: str = Field(max_length=500)
    old_value: Optional[str] = Field(default=None, max_length=1000)
    new_value: Optional[str] = Field(default=None, max_length=1000)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ModerationLogCreate(ModerationLogBase):
    moderator_id: Optional[UUID] = None


class ModerationLog(ModerationLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    moderator_id: Optional[UUID] = None
    created_at: datetime


class ModerationLogPublic(ModerationLogBase):
    id: UUID
    moderator_id: Optional[UUID] = None
    created_at: datetime


# Analytics and Dashboard Schemas
class ModerationStats(BaseModel):
    total_reports: int
    pending_reports: int
    resolved_reports: int
    total_actions: int
    active_bans: int
    total_strikes: int
    appeals_pending: int


class ContentModerationSummary(BaseModel):
    content_type: str
    total_items: int
    flagged_items: int
    moderated_items: int
    removal_rate: float


class ModeratorActivity(BaseModel):
    moderator_id: UUID
    moderator_name: str
    actions_taken: int
    reports_reviewed: int
    appeals_handled: int
    last_activity: datetime


# AI Moderation Schemas
class AIModerationRequest(BaseModel):
    content_type: str
    content_id: UUID
    content_text: Optional[str] = None
    content_url: Optional[str] = None
    check_types: List[str] = Field(
        default_factory=lambda: ["spam", "hate_speech", "fake_news"]
    )


class AIModerationResult(BaseModel):
    content_id: UUID
    flags: List[Dict[str, Any]]
    overall_risk_score: float
    recommended_action: str
    confidence_scores: Dict[str, float]


# Bulk Operations Schemas
class BulkModerationAction(BaseModel):
    content_ids: List[UUID]
    action_type: str
    reason: str
    severity: str = "medium"


class BulkReportUpdate(BaseModel):
    report_ids: List[UUID]
    status: str
    resolution: Optional[str] = None
