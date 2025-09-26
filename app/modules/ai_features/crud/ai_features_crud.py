from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, and_, delete, desc, func, or_, select, update

from app.modules.ai_features.model.ai_features import (
    AIModelMetrics,
    AnomalyDetection,
    ChurnPrediction,
    ContentAnalysis,
    ContentClassification,
    ContentRecommendation,
    EngagementPrediction,
    PersonalizedFeed,
    TranslationCache,
    TrendAnalysis,
    UserBehavior,
)
from app.modules.ai_features.schema.ai_features import (
    AIModelMetricsCreate,
    AIModelMetricsUpdate,
    AnomalyDetectionCreate,
    AnomalyDetectionUpdate,
    ChurnPredictionCreate,
    ChurnPredictionUpdate,
    ContentAnalysisCreate,
    ContentAnalysisUpdate,
    ContentClassificationCreate,
    ContentClassificationUpdate,
    ContentRecommendationCreate,
    ContentRecommendationUpdate,
    EngagementPredictionCreate,
    EngagementPredictionUpdate,
    PersonalizedFeedCreate,
    PersonalizedFeedUpdate,
    TranslationCacheCreate,
    TranslationCacheUpdate,
    TrendAnalysisCreate,
    TrendAnalysisUpdate,
    UserBehaviorCreate,
)
from app.shared.crud.base import CRUDBase


class CRUDContentRecommendation(
    CRUDBase[
        ContentRecommendation, ContentRecommendationCreate, ContentRecommendationUpdate
    ]
):
    def get_multi_by_user(
        self, session: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ContentRecommendation]:
        return session.exec(
            select(ContentRecommendation)
            .where(ContentRecommendation.user_id == user_id)
            .order_by(desc(ContentRecommendation.recommendation_score))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_unviewed_by_user(
        self, session: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ContentRecommendation]:
        return session.exec(
            select(ContentRecommendation)
            .where(
                and_(
                    ContentRecommendation.user_id == user_id,
                    ContentRecommendation.is_viewed == False,
                )
            )
            .order_by(desc(ContentRecommendation.recommendation_score))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_by_content_and_user(
        self, session: Session, *, user_id: UUID, content_type: str, content_id: UUID
    ) -> Optional[ContentRecommendation]:
        return session.exec(
            select(ContentRecommendation).where(
                and_(
                    ContentRecommendation.user_id == user_id,
                    ContentRecommendation.content_type == content_type,
                    ContentRecommendation.content_id == content_id,
                )
            )
        ).first()

    def mark_viewed(
        self, session: Session, *, user_id: UUID, content_type: str, content_id: UUID
    ) -> bool:
        result = session.exec(
            update(ContentRecommendation)
            .where(
                and_(
                    ContentRecommendation.user_id == user_id,
                    ContentRecommendation.content_type == content_type,
                    ContentRecommendation.content_id == content_id,
                    ContentRecommendation.is_viewed == False,
                )
            )
            .values(is_viewed=True, updated_at=datetime.utcnow())
        )
        session.commit()
        return result.rowcount > 0

    def mark_clicked(
        self, session: Session, *, user_id: UUID, content_type: str, content_id: UUID
    ) -> bool:
        result = session.exec(
            update(ContentRecommendation)
            .where(
                and_(
                    ContentRecommendation.user_id == user_id,
                    ContentRecommendation.content_type == content_type,
                    ContentRecommendation.content_id == content_id,
                )
            )
            .values(is_clicked=True, updated_at=datetime.utcnow())
        )
        session.commit()
        return result.rowcount > 0


class CRUDContentAnalysis(
    CRUDBase[ContentAnalysis, ContentAnalysisCreate, ContentAnalysisUpdate]
):
    def get_by_content_and_type(
        self,
        session: Session,
        *,
        content_type: str,
        content_id: UUID,
        analysis_type: str,
    ) -> Optional[ContentAnalysis]:
        return session.exec(
            select(ContentAnalysis).where(
                and_(
                    ContentAnalysis.content_type == content_type,
                    ContentAnalysis.content_id == content_id,
                    ContentAnalysis.analysis_type == analysis_type,
                    ContentAnalysis.is_active == True,
                )
            )
        ).first()

    def get_multi_by_content(
        self, session: Session, *, content_type: str, content_id: UUID
    ) -> List[ContentAnalysis]:
        return session.exec(
            select(ContentAnalysis).where(
                and_(
                    ContentAnalysis.content_type == content_type,
                    ContentAnalysis.content_id == content_id,
                    ContentAnalysis.is_active == True,
                )
            )
        ).all()

    def get_multi_by_type(
        self, session: Session, *, analysis_type: str, skip: int = 0, limit: int = 100
    ) -> List[ContentAnalysis]:
        return session.exec(
            select(ContentAnalysis)
            .where(ContentAnalysis.analysis_type == analysis_type)
            .order_by(desc(ContentAnalysis.created_at))
            .offset(skip)
            .limit(limit)
        ).all()

    def deactivate_old_analyses(
        self,
        session: Session,
        *,
        content_type: str,
        content_id: UUID,
        keep_latest: bool = True,
    ) -> int:
        """Deactivate old analyses for content, optionally keeping the latest one."""
        query = (
            select(ContentAnalysis)
            .where(
                and_(
                    ContentAnalysis.content_type == content_type,
                    ContentAnalysis.content_id == content_id,
                    ContentAnalysis.is_active == True,
                )
            )
            .order_by(desc(ContentAnalysis.created_at))
        )

        analyses = session.exec(query).all()

        if not analyses:
            return 0

        if keep_latest:
            # Keep only the latest analysis active
            analyses_to_deactivate = analyses[1:]
        else:
            # Deactivate all
            analyses_to_deactivate = analyses

        ids_to_deactivate = [a.id for a in analyses_to_deactivate]

        if ids_to_deactivate:
            result = session.exec(
                update(ContentAnalysis)
                .where(ContentAnalysis.id.in_(ids_to_deactivate))
                .values(is_active=False, updated_at=datetime.utcnow())
            )
            session.commit()
            return result.rowcount

        return 0


class CRUDUserBehavior(CRUDBase[UserBehavior, UserBehaviorCreate, None]):
    def get_multi_by_user(
        self, session: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[UserBehavior]:
        return session.exec(
            select(UserBehavior)
            .where(UserBehavior.user_id == user_id)
            .order_by(desc(UserBehavior.created_at))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_multi_by_action(
        self, session: Session, *, action_type: str, skip: int = 0, limit: int = 100
    ) -> List[UserBehavior]:
        return session.exec(
            select(UserBehavior)
            .where(UserBehavior.action_type == action_type)
            .order_by(desc(UserBehavior.created_at))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_recent_by_user(
        self, session: Session, *, user_id: UUID, hours: int = 24
    ) -> List[UserBehavior]:
        since = datetime.utcnow() - timedelta(hours=hours)
        return session.exec(
            select(UserBehavior)
            .where(
                and_(UserBehavior.user_id == user_id, UserBehavior.created_at >= since)
            )
            .order_by(desc(UserBehavior.created_at))
        ).all()

    def get_behavior_stats(
        self, session: Session, *, user_id: UUID, days: int = 30
    ) -> Dict[str, Any]:
        since = datetime.utcnow() - timedelta(days=days)

        # Get action counts
        actions_query = (
            select(UserBehavior.action_type, func.count(UserBehavior.id).label("count"))
            .where(
                and_(UserBehavior.user_id == user_id, UserBehavior.created_at >= since)
            )
            .group_by(UserBehavior.action_type)
        )

        actions_result = session.exec(actions_query).all()
        action_counts = {action: count for action, count in actions_result}

        # Get target type counts
        targets_query = (
            select(UserBehavior.target_type, func.count(UserBehavior.id).label("count"))
            .where(
                and_(UserBehavior.user_id == user_id, UserBehavior.created_at >= since)
            )
            .group_by(UserBehavior.target_type)
        )

        targets_result = session.exec(targets_query).all()
        target_counts = {target: count for target, count in targets_result}

        return {
            "action_counts": action_counts,
            "target_counts": target_counts,
            "total_actions": sum(action_counts.values()),
            "period_days": days,
        }


class CRUDPersonalizedFeed(
    CRUDBase[PersonalizedFeed, PersonalizedFeedCreate, PersonalizedFeedUpdate]
):
    def get_by_user(
        self, session: Session, *, user_id: UUID
    ) -> Optional[PersonalizedFeed]:
        return session.exec(
            select(PersonalizedFeed).where(
                and_(
                    PersonalizedFeed.user_id == user_id,
                    PersonalizedFeed.is_active == True,
                )
            )
        ).first()

    def get_active_feeds(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[PersonalizedFeed]:
        return session.exec(
            select(PersonalizedFeed)
            .where(PersonalizedFeed.is_active == True)
            .order_by(desc(PersonalizedFeed.last_updated))
            .offset(skip)
            .limit(limit)
        ).all()


class CRUDTrendAnalysis(
    CRUDBase[TrendAnalysis, TrendAnalysisCreate, TrendAnalysisUpdate]
):
    def get_trending(
        self,
        session: Session,
        *,
        trend_type: str,
        time_window: str,
        limit: int = 50,
        min_score: float = 0.0,
    ) -> List[TrendAnalysis]:
        return session.exec(
            select(TrendAnalysis)
            .where(
                and_(
                    TrendAnalysis.trend_type == trend_type,
                    TrendAnalysis.time_window == time_window,
                    TrendAnalysis.trend_score >= min_score,
                )
            )
            .order_by(desc(TrendAnalysis.trend_score))
            .limit(limit)
        ).all()

    def get_viral_trends(
        self, session: Session, *, time_window: str, limit: int = 20
    ) -> List[TrendAnalysis]:
        return session.exec(
            select(TrendAnalysis)
            .where(
                and_(
                    TrendAnalysis.time_window == time_window,
                    TrendAnalysis.is_viral == True,
                )
            )
            .order_by(desc(TrendAnalysis.trend_score))
            .limit(limit)
        ).all()

    def get_trend_by_value(
        self, session: Session, *, trend_type: str, trend_value: str, time_window: str
    ) -> Optional[TrendAnalysis]:
        return session.exec(
            select(TrendAnalysis).where(
                and_(
                    TrendAnalysis.trend_type == trend_type,
                    TrendAnalysis.trend_value == trend_value,
                    TrendAnalysis.time_window == time_window,
                )
            )
        ).first()


class CRUDContentClassification(
    CRUDBase[
        ContentClassification, ContentClassificationCreate, ContentClassificationUpdate
    ]
):
    def get_by_content(
        self, session: Session, *, content_type: str, content_id: UUID
    ) -> Optional[ContentClassification]:
        return session.exec(
            select(ContentClassification).where(
                and_(
                    ContentClassification.content_type == content_type,
                    ContentClassification.content_id == content_id,
                )
            )
        ).first()

    def get_by_category(
        self, session: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[ContentClassification]:
        return session.exec(
            select(ContentClassification)
            .where(ContentClassification.category == category)
            .order_by(desc(ContentClassification.confidence_score))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_high_confidence_classifications(
        self,
        session: Session,
        *,
        min_confidence: float = 0.8,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ContentClassification]:
        return session.exec(
            select(ContentClassification)
            .where(ContentClassification.confidence_score >= min_confidence)
            .order_by(desc(ContentClassification.confidence_score))
            .offset(skip)
            .limit(limit)
        ).all()


class CRUDAnomalyDetection(
    CRUDBase[AnomalyDetection, AnomalyDetectionCreate, AnomalyDetectionUpdate]
):
    def get_uninvestigated_anomalies(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[AnomalyDetection]:
        return session.exec(
            select(AnomalyDetection)
            .where(AnomalyDetection.is_investigated == False)
            .order_by(desc(AnomalyDetection.anomaly_score))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_anomalies_by_type(
        self, session: Session, *, anomaly_type: str, skip: int = 0, limit: int = 100
    ) -> List[AnomalyDetection]:
        return session.exec(
            select(AnomalyDetection)
            .where(AnomalyDetection.anomaly_type == anomaly_type)
            .order_by(desc(AnomalyDetection.anomaly_score))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_high_risk_anomalies(
        self,
        session: Session,
        *,
        min_score: float = 0.8,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AnomalyDetection]:
        return session.exec(
            select(AnomalyDetection)
            .where(AnomalyDetection.anomaly_score >= min_score)
            .order_by(desc(AnomalyDetection.anomaly_score))
            .offset(skip)
            .limit(limit)
        ).all()


class CRUDEngagementPrediction(
    CRUDBase[
        EngagementPrediction, EngagementPredictionCreate, EngagementPredictionUpdate
    ]
):
    def get_by_content(
        self, session: Session, *, content_type: str, content_id: UUID
    ) -> Optional[EngagementPrediction]:
        return session.exec(
            select(EngagementPrediction).where(
                and_(
                    EngagementPrediction.content_type == content_type,
                    EngagementPrediction.content_id == content_id,
                )
            )
        ).first()

    def get_viral_predictions(
        self,
        session: Session,
        *,
        min_probability: float = 0.7,
        skip: int = 0,
        limit: int = 100,
    ) -> List[EngagementPrediction]:
        return session.exec(
            select(EngagementPrediction)
            .where(EngagementPrediction.viral_probability >= min_probability)
            .order_by(desc(EngagementPrediction.viral_probability))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_predictions_by_score(
        self,
        session: Session,
        *,
        min_score: float = 0.5,
        skip: int = 0,
        limit: int = 100,
    ) -> List[EngagementPrediction]:
        return session.exec(
            select(EngagementPrediction)
            .where(EngagementPrediction.engagement_score >= min_score)
            .order_by(desc(EngagementPrediction.engagement_score))
            .offset(skip)
            .limit(limit)
        ).all()


class CRUDChurnPrediction(
    CRUDBase[ChurnPrediction, ChurnPredictionCreate, ChurnPredictionUpdate]
):
    def get_by_user(
        self, session: Session, *, user_id: UUID
    ) -> Optional[ChurnPrediction]:
        return session.exec(
            select(ChurnPrediction)
            .where(ChurnPrediction.user_id == user_id)
            .order_by(desc(ChurnPrediction.created_at))
        ).first()

    def get_high_risk_users(
        self,
        session: Session,
        *,
        min_probability: float = 0.7,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChurnPrediction]:
        return session.exec(
            select(ChurnPrediction)
            .where(ChurnPrediction.churn_probability >= min_probability)
            .order_by(desc(ChurnPrediction.churn_probability))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_churn_predictions_by_risk_level(
        self, session: Session, *, risk_level: str, skip: int = 0, limit: int = 100
    ) -> List[ChurnPrediction]:
        return session.exec(
            select(ChurnPrediction)
            .where(ChurnPrediction.churn_risk_level == risk_level)
            .order_by(desc(ChurnPrediction.churn_probability))
            .offset(skip)
            .limit(limit)
        ).all()


class CRUDTranslationCache(
    CRUDBase[TranslationCache, TranslationCacheCreate, TranslationCacheUpdate]
):
    def get_translation(
        self,
        session: Session,
        *,
        content_type: str,
        content_id: UUID,
        source_language: str,
        target_language: str,
    ) -> Optional[TranslationCache]:
        return session.exec(
            select(TranslationCache).where(
                and_(
                    TranslationCache.content_type == content_type,
                    TranslationCache.content_id == content_id,
                    TranslationCache.source_language == source_language,
                    TranslationCache.target_language == target_language,
                    TranslationCache.is_active == True,
                )
            )
        ).first()

    def get_translations_by_language(
        self, session: Session, *, target_language: str, skip: int = 0, limit: int = 100
    ) -> List[TranslationCache]:
        return session.exec(
            select(TranslationCache)
            .where(
                and_(
                    TranslationCache.target_language == target_language,
                    TranslationCache.is_active == True,
                )
            )
            .order_by(desc(TranslationCache.created_at))
            .offset(skip)
            .limit(limit)
        ).all()

    def cleanup_old_cache(self, session: Session, *, days_old: int = 30) -> int:
        """Remove translations older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        result = session.exec(
            update(TranslationCache)
            .where(
                and_(
                    TranslationCache.created_at < cutoff_date,
                    TranslationCache.is_active == True,
                )
            )
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        session.commit()
        return result.rowcount


class CRUDAIModelMetrics(
    CRUDBase[AIModelMetrics, AIModelMetricsCreate, AIModelMetricsUpdate]
):
    def get_metrics_by_model(
        self, session: Session, *, model_name: str, skip: int = 0, limit: int = 100
    ) -> List[AIModelMetrics]:
        return session.exec(
            select(AIModelMetrics)
            .where(AIModelMetrics.model_name == model_name)
            .order_by(desc(AIModelMetrics.evaluation_date))
            .offset(skip)
            .limit(limit)
        ).all()

    def get_latest_metrics(
        self, session: Session, *, model_name: str, model_version: Optional[str] = None
    ) -> Optional[AIModelMetrics]:
        query = select(AIModelMetrics).where(AIModelMetrics.model_name == model_name)

        if model_version:
            query = query.where(AIModelMetrics.model_version == model_version)

        return session.exec(
            query.order_by(desc(AIModelMetrics.evaluation_date))
        ).first()

    def get_baseline_metrics(
        self, session: Session, *, model_name: str
    ) -> Optional[AIModelMetrics]:
        return session.exec(
            select(AIModelMetrics)
            .where(
                and_(
                    AIModelMetrics.model_name == model_name,
                    AIModelMetrics.is_baseline == True,
                )
            )
            .order_by(desc(AIModelMetrics.evaluation_date))
        ).first()

    def get_metrics_by_type(
        self, session: Session, *, metric_type: str, skip: int = 0, limit: int = 100
    ) -> List[AIModelMetrics]:
        return session.exec(
            select(AIModelMetrics)
            .where(AIModelMetrics.metric_type == metric_type)
            .order_by(desc(AIModelMetrics.metric_value))
            .offset(skip)
            .limit(limit)
        ).all()


# CRUD instances
crud_content_recommendation = CRUDContentRecommendation(ContentRecommendation)
crud_content_analysis = CRUDContentAnalysis(ContentAnalysis)
crud_user_behavior = CRUDUserBehavior(UserBehavior)
crud_personalized_feed = CRUDPersonalizedFeed(PersonalizedFeed)
crud_trend_analysis = CRUDTrendAnalysis(TrendAnalysis)
crud_content_classification = CRUDContentClassification(ContentClassification)
crud_anomaly_detection = CRUDAnomalyDetection(AnomalyDetection)
crud_engagement_prediction = CRUDEngagementPrediction(EngagementPrediction)
crud_churn_prediction = CRUDChurnPrediction(ChurnPrediction)
crud_translation_cache = CRUDTranslationCache(TranslationCache)
crud_ai_model_metrics = CRUDAIModelMetrics(AIModelMetrics)
