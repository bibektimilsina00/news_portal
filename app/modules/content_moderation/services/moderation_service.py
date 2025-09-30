from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.content_moderation.crud.moderation_crud import (
    crud_ban_appeal,
    crud_content_flag,
    crud_content_report,
    crud_moderation_action,
    crud_moderation_appeal,
    crud_moderation_log,
    crud_user_ban,
    crud_user_strike,
)
from app.modules.content_moderation.model.moderation import (
    BanAppeal,
    ContentReport,
    ModerationAction,
    ModerationAppeal,
    UserBan,
    UserStrike,
)
from app.modules.content_moderation.schema.moderation import (
    AIModerationRequest,
    AIModerationResult,
    BanAppealCreate,
    BulkModerationAction,
    BulkReportUpdate,
    ContentFlagCreate,
    ContentModerationSummary,
    ContentReportCreate,
    ModerationActionCreate,
    ModerationAppealCreate,
    ModerationLogCreate,
    ModerationStats,
    ModeratorActivity,
    UserBanCreate,
    UserStrikeCreate,
)


class ContentModerationService:
    """Service for content moderation operations."""

    def __init__(self, session: Session):
        self.session = session

    async def report_content(
        self, reporter_id: UUID, report_data: ContentReportCreate
    ) -> ContentReport:
        """Create a new content report."""
        # Check if user has already reported this content
        existing_reports = crud_content_report.get_multi_by_content(
            self.session,
            content_type=report_data.content_type,
            content_id=report_data.content_id,
        )

        user_already_reported = any(
            r.reporter_id == reporter_id for r in existing_reports
        )
        if user_already_reported:
            raise ValueError("You have already reported this content")

        # Create the report
        report = crud_content_report.create(
            self.session,
            obj_in=ContentReportCreate(
                reporter_id=reporter_id, **report_data.model_dump()
            ),
        )

        # Log the report
        await self._log_moderation_action(
            moderator_id=None,
            action_type="content_reported",
            target_type="content_report",
            target_id=report.id,
            description=f"Content reported: {report_data.reason}",
            extra_data={
                "content_type": report_data.content_type,
                "content_id": str(report_data.content_id),
            },
        )

        return report

    async def review_report(
        self,
        report_id: UUID,
        moderator_id: UUID,
        status: str,
        resolution: Optional[str] = None,
    ) -> ContentReport:
        """Review and update a content report."""
        report = crud_content_report.update_status(
            self.session,
            id=report_id,
            status=status,
            reviewed_by=moderator_id,
            resolution=resolution,
        )

        if not report:
            raise ValueError("Report not found")

        # Log the review
        await self._log_moderation_action(
            moderator_id=moderator_id,
            action_type="report_reviewed",
            target_type="content_report",
            target_id=report_id,
            description=f"Report {status}: {resolution or 'No resolution provided'}",
            old_value=report.status,
            new_value=status,
        )

        return report

    async def take_moderation_action(
        self, moderator_id: UUID, action_data: ModerationActionCreate
    ) -> ModerationAction:
        """Take a moderation action on content."""
        # Create the action
        action = crud_moderation_action.create(
            self.session,
            obj_in=ModerationActionCreate(
                moderator_id=moderator_id, **action_data.model_dump()
            ),
        )

        # Set appeal deadline if applicable
        if action_data.duration_hours:
            action.appeal_deadline = datetime.utcnow() + timedelta(
                hours=action_data.duration_hours
            )
            self.session.add(action)
            self.session.commit()

        # Log the action
        await self._log_moderation_action(
            moderator_id=moderator_id,
            action_type="moderation_action_taken",
            target_type=action_data.content_type,
            target_id=action_data.content_id,
            description=f"Action taken: {action_data.action_type} - {action_data.reason}",
            extra_data={
                "action_type": action_data.action_type,
                "severity": action_data.severity,
            },
        )

        return action

    async def appeal_moderation_action(
        self, appellant_id: UUID, appeal_data: ModerationAppealCreate
    ) -> ModerationAppeal:
        """Create an appeal against a moderation action."""
        # Check if appeal already exists
        existing_appeals = crud_moderation_appeal.get_multi_by_action(
            self.session, action_id=appeal_data.action_id
        )

        user_already_appealed = any(
            a.appellant_id == appellant_id for a in existing_appeals
        )
        if user_already_appealed:
            raise ValueError("You have already appealed this action")

        # Create the appeal
        appeal = crud_moderation_appeal.create(
            self.session,
            obj_in=ModerationAppealCreate(
                appellant_id=appellant_id, **appeal_data.model_dump()
            ),
        )

        # Log the appeal
        await self._log_moderation_action(
            moderator_id=None,
            action_type="moderation_appeal_submitted",
            target_type="moderation_action",
            target_id=appeal_data.action_id,
            description=f"Appeal submitted: {appeal_data.reason[:100]}...",
            extra_data={"appeal_id": str(appeal.id)},
        )

        return appeal

    async def review_appeal(
        self,
        appeal_id: UUID,
        moderator_id: UUID,
        status: str,
        review_notes: Optional[str] = None,
    ) -> ModerationAppeal:
        """Review a moderation appeal."""
        appeal = crud_moderation_appeal.update_status(
            self.session,
            id=appeal_id,
            status=status,
            reviewed_by=moderator_id,
            review_notes=review_notes,
        )

        if not appeal:
            raise ValueError("Appeal not found")

        # Log the review
        await self._log_moderation_action(
            moderator_id=moderator_id,
            action_type="appeal_reviewed",
            target_type="moderation_appeal",
            target_id=appeal_id,
            description=f"Appeal {status}: {review_notes or 'No notes provided'}",
            old_value=appeal.status,
            new_value=status,
        )

        return appeal

    async def issue_user_strike(
        self, user_id: UUID, issuer_id: UUID, strike_data: UserStrikeCreate
    ) -> UserStrike:
        """Issue a strike to a user."""
        # Calculate total strikes
        existing_strikes = crud_user_strike.get_multi_by_user(
            self.session, user_id=user_id, active_only=True
        )
        total_strikes = len(existing_strikes) + 1

        strike = crud_user_strike.create(
            self.session,
            obj_in=UserStrikeCreate(
                user_id=user_id,
                issued_by=issuer_id,
                total_strikes=total_strikes,
                **strike_data.model_dump(),
            ),
        )

        # Check if user should be banned (e.g., 3 strikes)
        if total_strikes >= 3:
            await self.ban_user(
                user_id=user_id,
                banned_by=issuer_id,
                reason=f"Automatic ban after {total_strikes} strikes",
                ban_type="temporary",
                duration_hours=7 * 24,  # 1 week
            )

        # Log the strike
        await self._log_moderation_action(
            moderator_id=issuer_id,
            action_type="user_strike_issued",
            target_type="user",
            target_id=user_id,
            description=f"Strike issued: {strike_data.reason}",
            extra_data={
                "strike_count": strike.strike_count,
                "total_strikes": total_strikes,
            },
        )

        return strike

    async def ban_user(
        self,
        user_id: UUID,
        banned_by: UUID,
        reason: str,
        ban_type: str = "temporary",
        duration_hours: Optional[int] = None,
        appeal_allowed: bool = True,
    ) -> UserBan:
        """Ban a user."""
        # Check if user is already banned
        existing_ban = crud_user_ban.get_ban_by_user(self.session, user_id=user_id)
        if existing_ban:
            raise ValueError("User is already banned")

        expires_at = None
        if ban_type == "temporary" and duration_hours:
            expires_at = datetime.utcnow() + timedelta(hours=duration_hours)

        ban = crud_user_ban.create(
            self.session,
            obj_in=UserBanCreate(
                user_id=user_id,
                banned_by=banned_by,
                reason=reason,
                ban_type=ban_type,
                duration_hours=duration_hours,
                expires_at=expires_at,
                appeal_allowed=appeal_allowed,
            ),
        )

        # Log the ban
        await self._log_moderation_action(
            moderator_id=banned_by,
            action_type="user_banned",
            target_type="user",
            target_id=user_id,
            description=f"User banned: {reason}",
            extra_data={"ban_type": ban_type, "duration_hours": duration_hours},
        )

        return ban

    async def appeal_ban(
        self, appellant_id: UUID, appeal_data: BanAppealCreate
    ) -> BanAppeal:
        """Create an appeal against a ban."""
        # Check if appeal already exists
        existing_appeals = crud_ban_appeal.get_multi_by_ban(
            self.session, ban_id=appeal_data.ban_id
        )

        user_already_appealed = any(
            a.appellant_id == appellant_id for a in existing_appeals
        )
        if user_already_appealed:
            raise ValueError("You have already appealed this ban")

        appeal = crud_ban_appeal.create(
            self.session,
            obj_in=BanAppealCreate(
                appellant_id=appellant_id, **appeal_data.model_dump()
            ),
        )

        # Log the appeal
        await self._log_moderation_action(
            moderator_id=None,
            action_type="ban_appeal_submitted",
            target_type="user_ban",
            target_id=appeal_data.ban_id,
            description=f"Ban appeal submitted: {appeal_data.reason[:100]}...",
            extra_data={"appeal_id": str(appeal.id)},
        )

        return appeal

    async def ai_moderate_content(
        self, request: AIModerationRequest
    ) -> AIModerationResult:
        """Use AI to moderate content."""
        # This would integrate with external AI services
        # For now, return mock results
        flags = []
        confidence_scores = {}

        # Mock AI analysis
        for check_type in request.check_types:
            if check_type == "spam":
                confidence = Decimal("0.15")  # Low spam probability
                if confidence > Decimal("0.5"):
                    flags.append(
                        {
                            "type": "spam",
                            "confidence": float(confidence),
                            "reason": "Detected spam patterns",
                        }
                    )
                confidence_scores["spam"] = float(confidence)

            elif check_type == "hate_speech":
                confidence = Decimal("0.05")  # Very low hate speech probability
                if confidence > Decimal("0.7"):
                    flags.append(
                        {
                            "type": "hate_speech",
                            "confidence": float(confidence),
                            "reason": "Detected potentially harmful content",
                        }
                    )
                confidence_scores["hate_speech"] = float(confidence)

            elif check_type == "fake_news":
                confidence = Decimal("0.10")  # Low fake news probability
                if confidence > Decimal("0.6"):
                    flags.append(
                        {
                            "type": "fake_news",
                            "confidence": float(confidence),
                            "reason": "Content may contain misinformation",
                        }
                    )
                confidence_scores["fake_news"] = float(confidence)

        # Calculate overall risk score
        overall_risk = max(confidence_scores.values()) if confidence_scores else 0.0

        # Determine recommended action
        if overall_risk > 0.8:
            recommended_action = "remove"
        elif overall_risk > 0.5:
            recommended_action = "flag_for_review"
        else:
            recommended_action = "allow"

        result = AIModerationResult(
            content_id=request.content_id,
            flags=flags,
            overall_risk_score=overall_risk,
            recommended_action=recommended_action,
            confidence_scores=confidence_scores,
        )

        # Create content flags in database if any were detected
        for flag in flags:
            flag_obj = crud_content_flag.create(
                self.session,
                obj_in=ContentFlagCreate(
                    content_type=request.content_type,
                    content_id=request.content_id,
                    flag_type=flag["type"],
                    confidence_score=Decimal(str(flag["confidence"])),
                    detected_text=request.content_text,
                    flagged_by="ai_moderation_service",
                    extra_data={"ai_analysis": flag},
                ),
            )

        return result

    async def bulk_moderate_content(
        self, moderator_id: UUID, bulk_action: BulkModerationAction
    ) -> List[ModerationAction]:
        """Apply moderation action to multiple content items."""
        actions = []

        for content_id in bulk_action.content_ids:
            action = await self.take_moderation_action(
                moderator_id=moderator_id,
                action_data=ModerationActionCreate(
                    content_type=bulk_action.content_type,
                    content_id=content_id,
                    action_type=bulk_action.action_type,
                    reason=bulk_action.reason,
                    severity=bulk_action.severity,
                ),
            )
            actions.append(action)

        return actions

    async def bulk_update_reports(
        self, moderator_id: UUID, bulk_update: BulkReportUpdate
    ) -> List[ContentReport]:
        """Update multiple reports at once."""
        updated_reports = []

        for report_id in bulk_update.report_ids:
            report = await self.review_report(
                report_id=report_id,
                moderator_id=moderator_id,
                status=bulk_update.status,
                resolution=bulk_update.resolution,
            )
            updated_reports.append(report)

        return updated_reports

    def get_moderation_stats(self) -> ModerationStats:
        """Get moderation statistics."""
        total_reports = len(crud_content_report.get_multi(self.session))
        pending_reports = crud_content_report.get_pending_reports_count(self.session)
        resolved_reports = total_reports - pending_reports

        total_actions = len(crud_moderation_action.get_multi(self.session))
        active_bans = len(crud_user_ban.get_active_bans(self.session))
        total_strikes = len(crud_user_strike.get_multi(self.session))

        # Count pending appeals
        appeals_pending = len(
            crud_moderation_appeal.get_multi_by_status(self.session, status="pending")
        )

        return ModerationStats(
            total_reports=total_reports,
            pending_reports=pending_reports,
            resolved_reports=resolved_reports,
            total_actions=total_actions,
            active_bans=active_bans,
            total_strikes=total_strikes,
            appeals_pending=appeals_pending,
        )

    def get_content_moderation_summary(self) -> List[ContentModerationSummary]:
        """Get summary of moderated content by type."""
        # This would require more complex queries to aggregate data
        # For now, return mock data
        return [
            ContentModerationSummary(
                content_type="post",
                total_items=1000,
                flagged_items=50,
                moderated_items=25,
                removal_rate=0.025,
            ),
            ContentModerationSummary(
                content_type="news",
                total_items=500,
                flagged_items=10,
                moderated_items=5,
                removal_rate=0.01,
            ),
            ContentModerationSummary(
                content_type="comment",
                total_items=2000,
                flagged_items=100,
                moderated_items=75,
                removal_rate=0.0375,
            ),
        ]

    def get_moderator_activity(self, hours: int = 24) -> List[ModeratorActivity]:
        """Get recent moderator activity."""
        # This would require joining with user data
        # For now, return mock data
        return [
            ModeratorActivity(
                moderator_id=UUID("12345678-1234-5678-9012-123456789012"),
                moderator_name="Moderator One",
                actions_taken=15,
                reports_reviewed=8,
                appeals_handled=3,
                last_activity=datetime.utcnow() - timedelta(hours=2),
            ),
            ModeratorActivity(
                moderator_id=UUID("87654321-4321-8765-2109-876543210987"),
                moderator_name="Moderator Two",
                actions_taken=22,
                reports_reviewed=12,
                appeals_handled=5,
                last_activity=datetime.utcnow() - timedelta(hours=1),
            ),
        ]

    async def _log_moderation_action(
        self,
        moderator_id: Optional[UUID],
        action_type: str,
        target_type: str,
        target_id: UUID,
        description: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a moderation action."""
        crud_moderation_log.create(
            self.session,
            obj_in=ModerationLogCreate(
                moderator_id=moderator_id,
                action_type=action_type,
                target_type=target_type,
                target_id=target_id,
                description=description,
                old_value=old_value,
                new_value=new_value,
                extra_data=extra_data or {},
            ),
        )

    def cleanup_expired_items(self) -> Dict[str, int]:
        """Clean up expired strikes and bans."""
        expired_strikes = crud_user_strike.deactivate_expired_strikes(self.session)
        expired_bans = crud_user_ban.deactivate_expired_bans(self.session)

        return {"expired_strikes": expired_strikes, "expired_bans": expired_bans}


# Service instance
content_moderation_service = ContentModerationService
