from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, and_, delete, func, or_, select, update

from app.modules.content_moderation.model.moderation import (
    BanAppeal,
    ContentFlag,
    ContentReport,
    ModerationAction,
    ModerationAppeal,
    ModerationLog,
    ModerationRule,
    UserBan,
    UserStrike,
)
from app.modules.content_moderation.schema.moderation import (
    BanAppealCreate,
    BanAppealUpdate,
    ContentFlagCreate,
    ContentFlagUpdate,
    ContentReportCreate,
    ContentReportUpdate,
    ModerationActionCreate,
    ModerationActionUpdate,
    ModerationAppealCreate,
    ModerationAppealUpdate,
    ModerationLogCreate,
    ModerationRuleCreate,
    ModerationRuleUpdate,
    UserBanCreate,
    UserBanUpdate,
    UserStrikeCreate,
    UserStrikeUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDContentReport(
    CRUDBase[ContentReport, ContentReportCreate, ContentReportUpdate]
):
    def get_multi_by_status(
        self, session: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[ContentReport]:
        return session.exec(
            select(ContentReport)
            .where(ContentReport.status == status)
            .offset(skip)
            .limit(limit)
        ).all()

    def get_multi_by_reporter(
        self, session: Session, *, reporter_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ContentReport]:
        return session.exec(
            select(ContentReport)
            .where(ContentReport.reporter_id == reporter_id)
            .offset(skip)
            .limit(limit)
        ).all()

    def get_multi_by_content(
        self, session: Session, *, content_type: str, content_id: UUID
    ) -> List[ContentReport]:
        return session.exec(
            select(ContentReport).where(
                and_(
                    ContentReport.content_type == content_type,
                    ContentReport.content_id == content_id,
                )
            )
        ).all()

    def get_pending_reports_count(self, session: Session) -> int:
        return session.exec(
            select(func.count(ContentReport.id)).where(
                ContentReport.status == "pending"
            )
        ).one()

    def update_status(
        self,
        session: Session,
        *,
        id: UUID,
        status: str,
        reviewed_by: UUID,
        resolution: Optional[str] = None,
    ) -> ContentReport:
        db_obj = session.get(ContentReport, id)
        if db_obj:
            db_obj.status = status
            db_obj.reviewed_by = reviewed_by
            db_obj.reviewed_at = datetime.utcnow()
            if resolution:
                db_obj.resolution = resolution
            db_obj.updated_at = datetime.utcnow()
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj


class CRUDModerationAction(
    CRUDBase[ModerationAction, ModerationActionCreate, ModerationActionUpdate]
):
    def get_multi_by_moderator(
        self, session: Session, *, moderator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ModerationAction]:
        return session.exec(
            select(ModerationAction)
            .where(ModerationAction.moderator_id == moderator_id)
            .order_by(ModerationAction.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_multi_by_content(
        self, session: Session, *, content_type: str, content_id: UUID
    ) -> List[ModerationAction]:
        return session.exec(
            select(ModerationAction)
            .where(
                and_(
                    ModerationAction.content_type == content_type,
                    ModerationAction.content_id == content_id,
                )
            )
            .order_by(ModerationAction.created_at.desc())
        ).all()

    def get_recent_actions(
        self, session: Session, *, hours: int = 24, skip: int = 0, limit: int = 100
    ) -> List[ModerationAction]:
        since = datetime.utcnow() - timedelta(hours=hours)
        return session.exec(
            select(ModerationAction)
            .where(ModerationAction.created_at >= since)
            .order_by(ModerationAction.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()


class CRUDModerationAppeal(
    CRUDBase[ModerationAppeal, ModerationAppealCreate, ModerationAppealUpdate]
):
    def get_multi_by_status(
        self, session: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[ModerationAppeal]:
        return session.exec(
            select(ModerationAppeal)
            .where(ModerationAppeal.status == status)
            .order_by(ModerationAppeal.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_multi_by_appellant(
        self, session: Session, *, appellant_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ModerationAppeal]:
        return session.exec(
            select(ModerationAppeal)
            .where(ModerationAppeal.appellant_id == appellant_id)
            .order_by(ModerationAppeal.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_multi_by_action(
        self, session: Session, *, action_id: UUID
    ) -> List[ModerationAppeal]:
        return session.exec(
            select(ModerationAppeal)
            .where(ModerationAppeal.action_id == action_id)
            .order_by(ModerationAppeal.created_at.desc())
        ).all()

    def update_status(
        self,
        session: Session,
        *,
        id: UUID,
        status: str,
        reviewed_by: UUID,
        review_notes: Optional[str] = None,
    ) -> ModerationAppeal:
        db_obj = session.get(ModerationAppeal, id)
        if db_obj:
            db_obj.status = status
            db_obj.reviewed_by = reviewed_by
            db_obj.reviewed_at = datetime.utcnow()
            if review_notes:
                db_obj.review_notes = review_notes
            db_obj.updated_at = datetime.utcnow()
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj


class CRUDContentFlag(CRUDBase[ContentFlag, ContentFlagCreate, ContentFlagUpdate]):
    def get_multi_by_status(
        self, session: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[ContentFlag]:
        return session.exec(
            select(ContentFlag)
            .where(ContentFlag.status == status)
            .order_by(ContentFlag.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_multi_by_content(
        self, session: Session, *, content_type: str, content_id: UUID
    ) -> List[ContentFlag]:
        return session.exec(
            select(ContentFlag)
            .where(
                and_(
                    ContentFlag.content_type == content_type,
                    ContentFlag.content_id == content_id,
                )
            )
            .order_by(ContentFlag.created_at.desc())
        ).all()

    def get_high_confidence_flags(
        self,
        session: Session,
        *,
        min_confidence: float = 0.8,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ContentFlag]:
        return session.exec(
            select(ContentFlag)
            .where(
                and_(
                    ContentFlag.confidence_score >= min_confidence,
                    ContentFlag.status == "active",
                )
            )
            .order_by(ContentFlag.confidence_score.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def resolve_flag(
        self, session: Session, *, id: UUID, resolved_by: UUID, status: str = "resolved"
    ) -> ContentFlag:
        db_obj = session.get(ContentFlag, id)
        if db_obj:
            db_obj.status = status
            db_obj.resolved_by = resolved_by
            db_obj.resolved_at = datetime.utcnow()
            db_obj.updated_at = datetime.utcnow()
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj


class CRUDUserStrike(CRUDBase[UserStrike, UserStrikeCreate, UserStrikeUpdate]):
    def get_multi_by_user(
        self, session: Session, *, user_id: UUID, active_only: bool = False
    ) -> List[UserStrike]:
        query = select(UserStrike).where(UserStrike.user_id == user_id)
        if active_only:
            query = query.where(
                and_(
                    UserStrike.is_active == True,
                    or_(
                        UserStrike.expires_at.is_(None),
                        UserStrike.expires_at > datetime.utcnow(),
                    ),
                )
            )
        return session.exec(query.order_by(UserStrike.created_at.desc())).all()

    def get_active_strikes_count(self, session: Session, *, user_id: UUID) -> int:
        return session.exec(
            select(func.count(UserStrike.id)).where(
                and_(
                    UserStrike.user_id == user_id,
                    UserStrike.is_active == True,
                    or_(
                        UserStrike.expires_at.is_(None),
                        UserStrike.expires_at > datetime.utcnow(),
                    ),
                )
            )
        ).one()

    def deactivate_expired_strikes(self, session: Session) -> int:
        result = session.exec(
            update(UserStrike)
            .where(
                and_(
                    UserStrike.is_active == True,
                    UserStrike.expires_at.is_not(None),
                    UserStrike.expires_at <= datetime.utcnow(),
                )
            )
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        session.commit()
        return result.rowcount


class CRUDUserBan(CRUDBase[UserBan, UserBanCreate, UserBanUpdate]):
    def get_active_bans(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[UserBan]:
        return session.exec(
            select(UserBan)
            .where(
                and_(
                    UserBan.is_active == True,
                    or_(
                        UserBan.expires_at.is_(None),
                        UserBan.expires_at > datetime.utcnow(),
                    ),
                )
            )
            .order_by(UserBan.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_ban_by_user(self, session: Session, *, user_id: UUID) -> Optional[UserBan]:
        return session.exec(
            select(UserBan).where(
                and_(
                    UserBan.user_id == user_id,
                    UserBan.is_active == True,
                    or_(
                        UserBan.expires_at.is_(None),
                        UserBan.expires_at > datetime.utcnow(),
                    ),
                )
            )
        ).first()

    def deactivate_expired_bans(self, session: Session) -> int:
        result = session.exec(
            update(UserBan)
            .where(
                and_(
                    UserBan.is_active == True,
                    UserBan.expires_at.is_not(None),
                    UserBan.expires_at <= datetime.utcnow(),
                )
            )
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        session.commit()
        return result.rowcount


class CRUDBanAppeal(CRUDBase[BanAppeal, BanAppealCreate, BanAppealUpdate]):
    def get_multi_by_status(
        self, session: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[BanAppeal]:
        return session.exec(
            select(BanAppeal)
            .where(BanAppeal.status == status)
            .order_by(BanAppeal.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_multi_by_ban(self, session: Session, *, ban_id: UUID) -> List[BanAppeal]:
        return session.exec(
            select(BanAppeal)
            .where(BanAppeal.ban_id == ban_id)
            .order_by(BanAppeal.created_at.desc())
        ).all()

    def update_status(
        self,
        session: Session,
        *,
        id: UUID,
        status: str,
        reviewed_by: UUID,
        review_notes: Optional[str] = None,
    ) -> BanAppeal:
        db_obj = session.get(BanAppeal, id)
        if db_obj:
            db_obj.status = status
            db_obj.reviewed_by = reviewed_by
            db_obj.reviewed_at = datetime.utcnow()
            if review_notes:
                db_obj.review_notes = review_notes
            db_obj.updated_at = datetime.utcnow()
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj


class CRUDModerationRule(
    CRUDBase[ModerationRule, ModerationRuleCreate, ModerationRuleUpdate]
):
    def get_active_rules(self, session: Session) -> List[ModerationRule]:
        return session.exec(
            select(ModerationRule)
            .where(ModerationRule.is_active == True)
            .order_by(ModerationRule.category, ModerationRule.severity)
        ).all()

    def get_rules_by_category(
        self, session: Session, *, category: str
    ) -> List[ModerationRule]:
        return session.exec(
            select(ModerationRule)
            .where(
                and_(
                    ModerationRule.category == category,
                    ModerationRule.is_active == True,
                )
            )
            .order_by(ModerationRule.severity)
        ).all()


class CRUDModerationLog(CRUDBase[ModerationLog, ModerationLogCreate, None]):
    def get_recent_logs(
        self, session: Session, *, hours: int = 24, skip: int = 0, limit: int = 100
    ) -> List[ModerationLog]:
        since = datetime.utcnow() - timedelta(hours=hours)
        return session.exec(
            select(ModerationLog)
            .where(ModerationLog.created_at >= since)
            .order_by(ModerationLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_logs_by_moderator(
        self, session: Session, *, moderator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ModerationLog]:
        return session.exec(
            select(ModerationLog)
            .where(ModerationLog.moderator_id == moderator_id)
            .order_by(ModerationLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_logs_by_target(
        self,
        session: Session,
        *,
        target_type: str,
        target_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModerationLog]:
        return session.exec(
            select(ModerationLog)
            .where(
                and_(
                    ModerationLog.target_type == target_type,
                    ModerationLog.target_id == target_id,
                )
            )
            .order_by(ModerationLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()


# CRUD instances
crud_content_report = CRUDContentReport(ContentReport)
crud_moderation_action = CRUDModerationAction(ModerationAction)
crud_moderation_appeal = CRUDModerationAppeal(ModerationAppeal)
crud_content_flag = CRUDContentFlag(ContentFlag)
crud_user_strike = CRUDUserStrike(UserStrike)
crud_user_ban = CRUDUserBan(UserBan)
crud_ban_appeal = CRUDBanAppeal(BanAppeal)
crud_moderation_rule = CRUDModerationRule(ModerationRule)
crud_moderation_log = CRUDModerationLog(ModerationLog)
