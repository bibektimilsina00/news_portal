from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.modules.ai_features.schema.ai_features import (
    AIModelHealthCheck,
    AIModelMetricsCreate,
    AIModelMetricsPublic,
    AnomalyDetectionPublic,
    BulkAnalysisRequest,
    BulkAnalysisResponse,
    ChurnAnalysisResponse,
    ChurnPredictionPublic,
    ContentAnalysisRequest,
    ContentAnalysisResponse,
    ContentClassificationPublic,
    ContentRecommendationPublic,
    EngagementPredictionPublic,
    EngagementPredictionRequest,
    EngagementPredictionResponse,
    PersonalizedFeedCreate,
    PersonalizedFeedPublic,
    RecommendationRequest,
    TranslationRequest,
    TranslationResponse,
    TrendAnalysisResponse,
    UserBehavior,
)
from app.modules.ai_features.services.ai_features_service import AIFeaturesService
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter()


# Content Recommendations Endpoints
@router.post("/recommendations/", response_model=List[ContentRecommendationPublic])
async def get_recommendations(
    *, session: SessionDep, current_user: CurrentUser, request: RecommendationRequest
) -> List[ContentRecommendationPublic]:
    """Get personalized content recommendations."""
    service = AIFeaturesService(session)
    response = await service.generate_recommendations(request)
    return response.recommendations


@router.post("/recommendations/mark-viewed")
async def mark_recommendation_viewed(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_type: str = Query(..., description="Type of content"),
    content_id: UUID = Query(..., description="ID of the content"),
) -> Message:
    """Mark a recommendation as viewed."""
    from app.modules.ai_features.crud.ai_features_crud import (
        crud_content_recommendation,
    )

    success = crud_content_recommendation.mark_viewed(
        session,
        user_id=current_user.id,
        content_type=content_type,
        content_id=content_id,
    )

    if success:
        return Message(message="Recommendation marked as viewed")
    else:
        raise HTTPException(status_code=404, detail="Recommendation not found")


@router.post("/recommendations/mark-clicked")
async def mark_recommendation_clicked(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_type: str = Query(..., description="Type of content"),
    content_id: UUID = Query(..., description="ID of the content"),
) -> Message:
    """Mark a recommendation as clicked."""
    from app.modules.ai_features.crud.ai_features_crud import (
        crud_content_recommendation,
    )

    success = crud_content_recommendation.mark_clicked(
        session,
        user_id=current_user.id,
        content_type=content_type,
        content_id=content_id,
    )

    if success:
        return Message(message="Recommendation marked as clicked")
    else:
        raise HTTPException(status_code=404, detail="Recommendation not found")


# Content Analysis Endpoints
@router.post("/analyze/", response_model=ContentAnalysisResponse)
async def analyze_content(
    *, session: SessionDep, current_user: CurrentUser, request: ContentAnalysisRequest
) -> ContentAnalysisResponse:
    """Analyze content using AI models."""
    service = AIFeaturesService(session)
    return await service.analyze_content(request)


@router.post("/analyze/bulk", response_model=BulkAnalysisResponse)
async def bulk_analyze_content(
    *, session: SessionDep, current_user: CurrentUser, request: BulkAnalysisRequest
) -> BulkAnalysisResponse:
    """Analyze multiple content items in bulk."""
    service = AIFeaturesService(session)
    return await service.bulk_analyze_content(request)


# Translation Endpoints
@router.post("/translate/", response_model=TranslationResponse)
async def translate_content(
    *, session: SessionDep, current_user: CurrentUser, request: TranslationRequest
) -> TranslationResponse:
    """Translate content to target language."""
    service = AIFeaturesService(session)
    return await service.translate_content(request)


# Trend Analysis Endpoints
@router.get("/trends/", response_model=TrendAnalysisResponse)
async def get_trending_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    time_window: str = Query("24h", description="Time window (1h, 24h, 7d, 30d)"),
    region: Optional[str] = Query(None, description="Region filter (country code)"),
    limit: int = Query(50, ge=1, le=200),
) -> TrendAnalysisResponse:
    """Get trending content analysis."""
    service = AIFeaturesService(session)
    return await service.get_trending_content(time_window, region, limit)


# Engagement Prediction Endpoints
@router.post("/predict/engagement", response_model=EngagementPredictionResponse)
async def predict_engagement(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    request: EngagementPredictionRequest,
) -> EngagementPredictionResponse:
    """Predict engagement metrics for content."""
    service = AIFeaturesService(session)
    return await service.predict_engagement(request)


# Churn Analysis Endpoints
@router.get("/analyze/churn/{user_id}", response_model=ChurnAnalysisResponse)
async def analyze_churn_risk(
    *, session: SessionDep, current_user: CurrentUser, user_id: UUID
) -> ChurnAnalysisResponse:
    """Analyze churn risk for a user."""
    service = AIFeaturesService(session)
    return await service.analyze_churn_risk(user_id)


# Personalized Feed Endpoints
@router.get("/feed/personalized", response_model=Optional[PersonalizedFeedPublic])
def get_personalized_feed(
    *, session: SessionDep, current_user: CurrentUser
) -> Optional[PersonalizedFeedPublic]:
    """Get user's personalized feed settings."""
    service = AIFeaturesService(session)
    return service.get_personalized_feed(current_user.id)


@router.post("/feed/personalized", response_model=PersonalizedFeedPublic)
def update_personalized_feed(
    *, session: SessionDep, current_user: CurrentUser, feed_data: PersonalizedFeedCreate
) -> PersonalizedFeedPublic:
    """Update personalized feed settings."""
    service = AIFeaturesService(session)
    return service.update_personalized_feed(current_user.id, feed_data)


# User Behavior Tracking Endpoints
@router.post("/behavior/track")
async def track_user_behavior(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    action_type: str = Query(..., description="Type of action performed"),
    target_type: str = Query(..., description="Type of target (post, user, etc.)"),
    target_id: UUID = Query(..., description="ID of the target"),
    session_id: Optional[str] = Query(None, description="User session ID"),
    device_info: Optional[Dict[str, Any]] = None,
    location_info: Optional[Dict[str, Any]] = None,
    duration_seconds: Optional[int] = Query(None, description="Duration in seconds"),
) -> Message:
    """Track user behavior for ML training."""
    from app.modules.ai_features.schema.ai_features import UserBehaviorCreate

    behavior_data = UserBehaviorCreate(
        user_id=current_user.id,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        session_id=session_id,
        device_info=device_info or {},
        location_info=location_info or {},
        duration_seconds=duration_seconds,
    )

    service = AIFeaturesService(session)
    service.track_user_behavior(behavior_data)

    return Message(message="User behavior tracked successfully")


# Content Classification Endpoints
@router.post("/classify/", response_model=ContentClassificationPublic)
def classify_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_type: str = Query(..., description="Type of content"),
    content_id: UUID = Query(..., description="ID of the content"),
    text: str = Query(..., description="Content text to classify"),
) -> ContentClassificationPublic:
    """Classify content into categories."""
    service = AIFeaturesService(session)
    return service.classify_content(content_type, content_id, text)


# Anomaly Detection Endpoints
@router.post("/detect-anomalies/", response_model=List[AnomalyDetectionPublic])
async def detect_anomalies(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    target_type: str = Query(..., description="Type of target to analyze"),
    target_id: UUID = Query(..., description="ID of the target"),
) -> List[AnomalyDetectionPublic]:
    """Detect anomalies for a target."""
    service = AIFeaturesService(session)
    return await service.detect_anomalies(target_type, target_id)


# AI Model Health and Metrics Endpoints
@router.get("/health/models", response_model=List[AIModelHealthCheck])
def get_ai_model_health(
    *, session: SessionDep, current_user: CurrentUser
) -> List[AIModelHealthCheck]:
    """Get health status of AI models."""
    service = AIFeaturesService(session)
    return service.get_ai_model_health()


@router.post("/metrics/log", response_model=AIModelMetricsPublic)
def log_model_metrics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    metrics_data: AIModelMetricsCreate,
) -> AIModelMetricsPublic:
    """Log performance metrics for AI models."""
    service = AIFeaturesService(session)
    return service.log_model_metrics(metrics_data)


@router.get("/metrics/{model_name}", response_model=List[AIModelMetricsPublic])
def get_model_metrics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    model_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[AIModelMetricsPublic]:
    """Get metrics for a specific AI model."""
    from app.modules.ai_features.crud.ai_features_crud import crud_ai_model_metrics

    return [
        AIModelMetricsPublic.model_validate(metric)
        for metric in crud_ai_model_metrics.get_metrics_by_model(
            session, model_name=model_name, skip=skip, limit=limit
        )
    ]


# Analytics and Insights Endpoints
@router.get("/analytics/user-behavior")
def get_user_behavior_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: Optional[UUID] = Query(
        None, description="User ID (optional, defaults to current user)"
    ),
    days: int = Query(30, ge=1, le=365),
) -> Dict[str, Any]:
    """Get user behavior analytics."""
    target_user_id = user_id or current_user.id

    from app.modules.ai_features.crud.ai_features_crud import crud_user_behavior

    return crud_user_behavior.get_behavior_stats(
        session, user_id=target_user_id, days=days
    )


@router.get("/analytics/content-classifications")
def get_content_classifications(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[ContentClassificationPublic]:
    """Get content classification analytics."""
    from app.modules.ai_features.crud.ai_features_crud import (
        crud_content_classification,
    )

    if category:
        classifications = crud_content_classification.get_by_category(
            session, category=category, skip=skip, limit=limit
        )
    else:
        classifications = crud_content_classification.get_multi(
            session, skip=skip, limit=limit
        )

    return [ContentClassificationPublic.model_validate(cls) for cls in classifications]


@router.get("/analytics/anomalies")
def get_anomaly_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    anomaly_type: Optional[str] = Query(None, description="Filter by anomaly type"),
    high_risk_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[AnomalyDetectionPublic]:
    """Get anomaly detection analytics."""
    from app.modules.ai_features.crud.ai_features_crud import crud_anomaly_detection

    if high_risk_only:
        anomalies = crud_anomaly_detection.get_high_risk_anomalies(
            session, min_score=0.8, skip=skip, limit=limit
        )
    elif anomaly_type:
        anomalies = crud_anomaly_detection.get_anomalies_by_type(
            session, anomaly_type=anomaly_type, skip=skip, limit=limit
        )
    else:
        anomalies = crud_anomaly_detection.get_multi(session, skip=skip, limit=limit)

    return [AnomalyDetectionPublic.model_validate(anomaly) for anomaly in anomalies]


@router.get("/analytics/engagement-predictions")
def get_engagement_predictions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    viral_only: bool = Query(False),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[EngagementPredictionPublic]:
    """Get engagement prediction analytics."""
    from app.modules.ai_features.crud.ai_features_crud import crud_engagement_prediction

    if viral_only:
        predictions = crud_engagement_prediction.get_viral_predictions(
            session, min_probability=0.7, skip=skip, limit=limit
        )
    else:
        predictions = crud_engagement_prediction.get_predictions_by_score(
            session, min_score=min_score, skip=skip, limit=limit
        )

    return [EngagementPredictionPublic.model_validate(pred) for pred in predictions]


@router.get("/analytics/churn-risks")
def get_churn_risk_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    min_probability: float = Query(0.0, ge=0.0, le=1.0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[ChurnAnalysisResponse]:
    """Get churn risk analytics."""
    from app.modules.ai_features.crud.ai_features_crud import crud_churn_prediction

    if risk_level:
        predictions = crud_churn_prediction.get_churn_predictions_by_risk_level(
            session, risk_level=risk_level, skip=skip, limit=limit
        )
    else:
        predictions = crud_churn_prediction.get_high_risk_users(
            session, min_probability=min_probability, skip=skip, limit=limit
        )

    responses = []
    for pred in predictions:
        responses.append(
            ChurnAnalysisResponse(
                user_id=pred.user_id,
                churn_risk=ChurnPredictionPublic.model_validate(pred),
                risk_factors=["Low activity", "Decreased engagement"],
                recommended_actions=[
                    "Send personalized recommendations",
                    "Offer premium features",
                ],
            )
        )

    return responses


# Utility Endpoints
@router.post("/cache/cleanup-translations")
def cleanup_translation_cache(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    days_old: int = Query(
        30, description="Remove translations older than this many days"
    ),
) -> Dict[str, int]:
    """Clean up old translation cache entries."""
    from app.modules.ai_features.crud.ai_features_crud import crud_translation_cache

    removed_count = crud_translation_cache.cleanup_old_cache(session, days_old=days_old)
    return {"removed_translations": removed_count}


@router.post("/analysis/deactivate-old")
def deactivate_old_analyses(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_type: str = Query(..., description="Type of content"),
    content_id: UUID = Query(..., description="ID of the content"),
) -> Dict[str, int]:
    """Deactivate old analyses for content."""
    from app.modules.ai_features.crud.ai_features_crud import crud_content_analysis

    deactivated_count = crud_content_analysis.deactivate_old_analyses(
        session, content_type=content_type, content_id=content_id
    )
    return {"deactivated_analyses": deactivated_count}
