from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.modules.content_moderation.schema.moderation import (
    AIModerationRequest,
    AIModerationResult,
    BanAppeal,
    BanAppealCreate,
    BanAppealPublic,
    BulkModerationAction,
    BulkReportUpdate,
    ContentFlag,
    ContentFlagPublic,
    ContentModerationSummary,
    ContentReport,
    ContentReportCreate,
    ContentReportPublic,
    ContentReportUpdate,
    ModerationAction,
    ModerationActionCreate,
    ModerationActionPublic,
    ModerationAppeal,
    ModerationAppealCreate,
    ModerationAppealPublic,
    ModerationLog,
    ModerationLogPublic,
    ModerationRule,
    ModerationRuleCreate,
    ModerationRulePublic,
    ModerationStats,
    ModeratorActivity,
    UserBan,
    UserBanCreate,
    UserBanPublic,
    UserStrike,
    UserStrikeCreate,
    UserStrikePublic,
)
from app.modules.content_moderation.services.moderation_service import (
    ContentModerationService,
)
from app.shared.deps.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.shared.schema.message import Message

router = APIRouter()


# Content Reporting Endpoints
@router.post("/reports/", response_model=ContentReportPublic)
async def report_content(
    *, session: SessionDep, current_user: CurrentUser, report_data: ContentReportCreate
) -> ContentReport:
    """Report content for moderation."""
    service = ContentModerationService(session)
    return await service.report_content(current_user.id, report_data)


@router.get("/reports/", response_model=List[ContentReportPublic])
def get_reports(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: None = Depends(get_current_active_superuser),  # Only moderators can view reports
) -> List[ContentReport]:
    """Get content reports (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_content_report

    if status_filter:
        return crud_content_report.get_multi_by_status(
            session, status=status_filter, skip=skip, limit=limit
        )
    return crud_content_report.get_multi(session, skip=skip, limit=limit)


@router.get("/reports/my-reports", response_model=List[ContentReportPublic])
def get_my_reports(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[ContentReport]:
    """Get reports submitted by current user."""
    from app.modules.content_moderation.crud.moderation_crud import crud_content_report

    return crud_content_report.get_multi_by_reporter(
        session, reporter_id=current_user.id, skip=skip, limit=limit
    )


@router.put("/reports/{report_id}/review", response_model=ContentReportPublic)
async def review_report(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    report_id: UUID,
    status: str = Query(..., description="New status for the report"),
    resolution: Optional[str] = Query(None, description="Resolution notes"),
    _: None = Depends(get_current_active_superuser),  # Only moderators can review
) -> ContentReport:
    """Review a content report (moderators only)."""
    service = ContentModerationService(session)
    return await service.review_report(report_id, current_user.id, status, resolution)


@router.post("/reports/bulk-update", response_model=List[ContentReportPublic])
async def bulk_update_reports(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    bulk_update: BulkReportUpdate,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ContentReport]:
    """Bulk update multiple reports (moderators only)."""
    service = ContentModerationService(session)
    return await service.bulk_update_reports(current_user.id, bulk_update)


# Moderation Actions Endpoints
@router.post("/actions/", response_model=ModerationActionPublic)
async def take_moderation_action(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    action_data: ModerationActionCreate,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> ModerationAction:
    """Take a moderation action (moderators only)."""
    service = ContentModerationService(session)
    return await service.take_moderation_action(current_user.id, action_data)


@router.get("/actions/", response_model=List[ModerationActionPublic])
def get_moderation_actions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_type: Optional[str] = Query(None),
    content_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ModerationAction]:
    """Get moderation actions (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import (
        crud_moderation_action,
    )

    if content_type and content_id:
        return crud_moderation_action.get_multi_by_content(
            session, content_type=content_type, content_id=content_id
        )
    return crud_moderation_action.get_multi(session, skip=skip, limit=limit)


@router.post("/actions/bulk", response_model=List[ModerationActionPublic])
async def bulk_moderate_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    bulk_action: BulkModerationAction,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ModerationAction]:
    """Apply moderation action to multiple content items (moderators only)."""
    service = ContentModerationService(session)
    return await service.bulk_moderate_content(current_user.id, bulk_action)


# Appeals Endpoints
@router.post("/appeals/", response_model=ModerationAppealPublic)
async def appeal_moderation_action(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    appeal_data: ModerationAppealCreate,
) -> ModerationAppeal:
    """Appeal a moderation action."""
    service = ContentModerationService(session)
    return await service.appeal_moderation_action(current_user.id, appeal_data)


@router.get("/appeals/", response_model=List[ModerationAppealPublic])
def get_appeals(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ModerationAppeal]:
    """Get moderation appeals (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import (
        crud_moderation_appeal,
    )

    if status_filter:
        return crud_moderation_appeal.get_multi_by_status(
            session, status=status_filter, skip=skip, limit=limit
        )
    return crud_moderation_appeal.get_multi(session, skip=skip, limit=limit)


@router.get("/appeals/my-appeals", response_model=List[ModerationAppealPublic])
def get_my_appeals(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[ModerationAppeal]:
    """Get appeals submitted by current user."""
    from app.modules.content_moderation.crud.moderation_crud import (
        crud_moderation_appeal,
    )

    return crud_moderation_appeal.get_multi_by_appellant(
        session, appellant_id=current_user.id, skip=skip, limit=limit
    )


@router.put("/appeals/{appeal_id}/review", response_model=ModerationAppealPublic)
async def review_appeal(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    appeal_id: UUID,
    status: str = Query(..., description="New status for the appeal"),
    review_notes: Optional[str] = Query(None, description="Review notes"),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> ModerationAppeal:
    """Review a moderation appeal (moderators only)."""
    service = ContentModerationService(session)
    return await service.review_appeal(appeal_id, current_user.id, status, review_notes)


# User Strikes Endpoints
@router.post("/strikes/", response_model=UserStrikePublic)
async def issue_user_strike(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    strike_data: UserStrikeCreate,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> UserStrike:
    """Issue a strike to a user (moderators only)."""
    service = ContentModerationService(session)
    return await service.issue_user_strike(
        strike_data.user_id, current_user.id, strike_data
    )


@router.get("/strikes/", response_model=List[UserStrikePublic])
def get_user_strikes(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: Optional[UUID] = Query(None),
    active_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[UserStrike]:
    """Get user strikes (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_user_strike

    if user_id:
        return crud_user_strike.get_multi_by_user(
            session, user_id=user_id, active_only=active_only
        )
    return crud_user_strike.get_multi(session, skip=skip, limit=limit)


# User Bans Endpoints
@router.post("/bans/", response_model=UserBanPublic)
async def ban_user(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    ban_data: UserBanCreate,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> UserBan:
    """Ban a user (moderators only)."""
    service = ContentModerationService(session)
    return await service.ban_user(
        ban_data.user_id,
        current_user.id,
        ban_data.reason,
        ban_data.ban_type,
        ban_data.duration_hours,
        ban_data.appeal_allowed,
    )


@router.get("/bans/", response_model=List[UserBanPublic])
def get_user_bans(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[UserBan]:
    """Get user bans (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_user_ban

    if active_only:
        return crud_user_ban.get_active_bans(session, skip=skip, limit=limit)
    return crud_user_ban.get_multi(session, skip=skip, limit=limit)


@router.post("/bans/appeal", response_model=BanAppealPublic)
async def appeal_ban(
    *, session: SessionDep, current_user: CurrentUser, appeal_data: BanAppealCreate
) -> BanAppeal:
    """Appeal a user ban."""
    service = ContentModerationService(session)
    return await service.appeal_ban(current_user.id, appeal_data)


@router.get("/bans/appeals", response_model=List[BanAppealPublic])
def get_ban_appeals(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[BanAppeal]:
    """Get ban appeals (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_ban_appeal

    if status_filter:
        return crud_ban_appeal.get_multi_by_status(
            session, status=status_filter, skip=skip, limit=limit
        )
    return crud_ban_appeal.get_multi(session, skip=skip, limit=limit)


# AI Moderation Endpoints
@router.post("/ai-moderate", response_model=AIModerationResult)
async def ai_moderate_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    request: AIModerationRequest,
    _: None = Depends(get_current_active_superuser),  # Only moderators for now
) -> AIModerationResult:
    """Use AI to moderate content (moderators only)."""
    service = ContentModerationService(session)
    return await service.ai_moderate_content(request)


# Content Flags Endpoints
@router.get("/flags/", response_model=List[ContentFlagPublic])
def get_content_flags(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    status_filter: Optional[str] = Query(None, alias="status"),
    high_confidence_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ContentFlag]:
    """Get content flags (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_content_flag

    if high_confidence_only:
        return crud_content_flag.get_high_confidence_flags(
            session, min_confidence=0.8, skip=skip, limit=limit
        )
    elif status_filter:
        return crud_content_flag.get_multi_by_status(
            session, status=status_filter, skip=skip, limit=limit
        )
    return crud_content_flag.get_multi(session, skip=skip, limit=limit)


@router.put("/flags/{flag_id}/resolve", response_model=ContentFlagPublic)
def resolve_content_flag(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    flag_id: UUID,
    status: str = Query("resolved", description="Resolution status"),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> ContentFlag:
    """Resolve a content flag (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_content_flag

    return crud_content_flag.resolve_flag(
        session, id=flag_id, resolved_by=current_user.id, status=status
    )


# Moderation Rules Endpoints
@router.post("/rules/", response_model=ModerationRulePublic)
def create_moderation_rule(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    rule_data: ModerationRuleCreate,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> ModerationRule:
    """Create a moderation rule (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_moderation_rule

    return crud_moderation_rule.create(session, obj_in=rule_data)


@router.get("/rules/", response_model=List[ModerationRulePublic])
def get_moderation_rules(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ModerationRule]:
    """Get moderation rules (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_moderation_rule

    if category:
        return crud_moderation_rule.get_rules_by_category(session, category=category)
    if active_only:
        return crud_moderation_rule.get_active_rules(session)
    return crud_moderation_rule.get_multi(session)


# Analytics and Dashboard Endpoints
@router.get("/stats", response_model=ModerationStats)
def get_moderation_stats(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> ModerationStats:
    """Get moderation statistics (moderators only)."""
    service = ContentModerationService(session)
    return service.get_moderation_stats()


@router.get("/analytics/content-summary", response_model=List[ContentModerationSummary])
def get_content_moderation_summary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ContentModerationSummary]:
    """Get content moderation summary (moderators only)."""
    service = ContentModerationService(session)
    return service.get_content_moderation_summary()


@router.get("/analytics/moderator-activity", response_model=List[ModeratorActivity])
def get_moderator_activity(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    hours: int = Query(24, description="Hours to look back"),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ModeratorActivity]:
    """Get moderator activity (moderators only)."""
    service = ContentModerationService(session)
    return service.get_moderator_activity(hours)


# Moderation Logs Endpoints
@router.get("/logs/", response_model=List[ModerationLogPublic])
def get_moderation_logs(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    hours: int = Query(24, description="Hours to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> List[ModerationLog]:
    """Get moderation logs (moderators only)."""
    from app.modules.content_moderation.crud.moderation_crud import crud_moderation_log

    return crud_moderation_log.get_recent_logs(
        session, hours=hours, skip=skip, limit=limit
    )


# Utility Endpoints
@router.post("/cleanup", response_model=Dict[str, int])
def cleanup_expired_items(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    _: None = Depends(get_current_active_superuser),  # Only moderators
) -> Dict[str, int]:
    """Clean up expired strikes and bans (moderators only)."""
    service = ContentModerationService(session)
    return service.cleanup_expired_items()


@router.get("/check-ban/{user_id}")
def check_user_ban(
    *, session: SessionDep, current_user: CurrentUser, user_id: UUID
) -> Dict[str, Any]:
    """Check if a user is currently banned."""
    from app.modules.content_moderation.crud.moderation_crud import crud_user_ban

    ban = crud_user_ban.get_ban_by_user(session, user_id=user_id)
    if ban:
        return {
            "is_banned": True,
            "ban_type": ban.ban_type,
            "reason": ban.reason,
            "expires_at": ban.expires_at,
            "appeal_allowed": ban.appeal_allowed,
        }
    return {"is_banned": False}
