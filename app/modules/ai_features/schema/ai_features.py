from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import SQLModel


# Content Recommendation Schemas
class ContentRecommendationBase(SQLModel):
    content_type: str = Field(max_length=50)
    content_id: UUID
    recommendation_score: Decimal = Field(max_digits=5, decimal_places=4)
    recommendation_reason: str = Field(max_length=100)
    algorithm_version: str = Field(max_length=50)
    position: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ContentRecommendationCreate(ContentRecommendationBase):
    user_id: UUID


class ContentRecommendationUpdate(SQLModel):
    is_viewed: Optional[bool] = None
    is_clicked: Optional[bool] = None
    position: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None


class ContentRecommendation(ContentRecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    is_viewed: bool
    is_clicked: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContentRecommendationPublic(ContentRecommendationBase):
    id: UUID
    user_id: UUID
    is_viewed: bool
    is_clicked: bool
    created_at: datetime


# Content Analysis Schemas
class ContentAnalysisBase(SQLModel):
    content_type: str = Field(max_length=50)
    content_id: UUID
    analysis_type: str = Field(max_length=50)
    analysis_result: Dict[str, Any]
    confidence_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    model_version: str = Field(max_length=50)
    processing_time_ms: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ContentAnalysisCreate(ContentAnalysisBase):
    pass


class ContentAnalysisUpdate(SQLModel):
    analysis_result: Optional[Dict[str, Any]] = None
    confidence_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    processing_time_ms: Optional[int] = None
    is_active: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class ContentAnalysis(ContentAnalysisBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContentAnalysisPublic(ContentAnalysisBase):
    id: UUID
    is_active: bool
    created_at: datetime


# User Behavior Schemas
class UserBehaviorBase(SQLModel):
    action_type: str = Field(max_length=50)
    target_type: str = Field(max_length=50)
    target_id: UUID
    session_id: Optional[str] = Field(default=None, max_length=100)
    device_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    location_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    duration_seconds: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserBehaviorCreate(UserBehaviorBase):
    user_id: UUID


class UserBehavior(UserBehaviorBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime


class UserBehaviorPublic(UserBehaviorBase):
    id: UUID
    user_id: UUID
    created_at: datetime


# Personalized Feed Schemas
class PersonalizedFeedBase(SQLModel):
    feed_algorithm: str = Field(default="collaborative_filtering", max_length=50)
    content_categories: List[str] = Field(default_factory=list)
    preferred_sources: List[str] = Field(default_factory=list)
    excluded_topics: List[str] = Field(default_factory=list)
    language_preferences: List[str] = Field(default_factory=list)
    time_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PersonalizedFeedCreate(PersonalizedFeedBase):
    user_id: UUID


class PersonalizedFeedUpdate(SQLModel):
    feed_algorithm: Optional[str] = Field(default=None, max_length=50)
    content_categories: Optional[List[str]] = None
    preferred_sources: Optional[List[str]] = None
    excluded_topics: Optional[List[str]] = None
    language_preferences: Optional[List[str]] = None
    time_preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class PersonalizedFeed(PersonalizedFeedBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    is_active: bool
    last_updated: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None


class PersonalizedFeedPublic(PersonalizedFeedBase):
    id: UUID
    user_id: UUID
    is_active: bool
    last_updated: datetime
    created_at: datetime


# Trend Analysis Schemas
class TrendAnalysisBase(SQLModel):
    trend_type: str = Field(max_length=50)
    trend_value: str = Field(max_length=200)
    trend_score: Decimal = Field(max_digits=8, decimal_places=4)
    growth_rate: Decimal = Field(max_digits=6, decimal_places=4)
    prediction_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    time_window: str = Field(max_length=20)
    region: Optional[str] = Field(default=None, max_length=10)
    language: Optional[str] = Field(default=None, max_length=10)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TrendAnalysisCreate(TrendAnalysisBase):
    pass


class TrendAnalysisUpdate(SQLModel):
    trend_score: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=4)
    growth_rate: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=4)
    prediction_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    is_viral: Optional[bool] = None
    peak_time: Optional[datetime] = None
    extra_data: Optional[Dict[str, Any]] = None


class TrendAnalysis(TrendAnalysisBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_viral: bool
    peak_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class TrendAnalysisPublic(TrendAnalysisBase):
    id: UUID
    is_viral: bool
    peak_time: Optional[datetime] = None
    created_at: datetime


# Content Classification Schemas
class ContentClassificationBase(SQLModel):
    content_type: str = Field(max_length=50)
    content_id: UUID
    category: str = Field(max_length=100)
    subcategory: Optional[str] = Field(default=None, max_length=100)
    confidence_score: Decimal = Field(max_digits=5, decimal_places=4)
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    sentiment_score: Optional[Decimal] = Field(
        default=None, max_digits=3, decimal_places=2
    )
    toxicity_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    model_version: str = Field(max_length=50)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ContentClassificationCreate(ContentClassificationBase):
    pass


class ContentClassificationUpdate(SQLModel):
    category: Optional[str] = Field(default=None, max_length=100)
    subcategory: Optional[str] = Field(default=None, max_length=100)
    confidence_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    sentiment_score: Optional[Decimal] = Field(
        default=None, max_digits=3, decimal_places=2
    )
    toxicity_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    extra_data: Optional[Dict[str, Any]] = None


class ContentClassification(ContentClassificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContentClassificationPublic(ContentClassificationBase):
    id: UUID
    created_at: datetime


# Anomaly Detection Schemas
class AnomalyDetectionBase(SQLModel):
    target_type: str = Field(max_length=50)
    target_id: UUID
    anomaly_type: str = Field(max_length=50)
    anomaly_score: Decimal = Field(max_digits=5, decimal_places=4)
    threshold_breached: Decimal = Field(max_digits=5, decimal_places=4)
    detection_method: str = Field(max_length=50)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AnomalyDetectionCreate(AnomalyDetectionBase):
    pass


class AnomalyDetectionUpdate(SQLModel):
    is_investigated: Optional[bool] = None
    investigation_result: Optional[str] = Field(default=None, max_length=200)
    false_positive: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class AnomalyDetection(AnomalyDetectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_investigated: bool
    investigation_result: Optional[str] = None
    false_positive: Optional[bool] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AnomalyDetectionPublic(AnomalyDetectionBase):
    id: UUID
    is_investigated: bool
    investigation_result: Optional[str] = None
    false_positive: Optional[bool] = None
    created_at: datetime


# Engagement Prediction Schemas
class EngagementPredictionBase(SQLModel):
    content_type: str = Field(max_length=50)
    content_id: UUID
    predicted_views: Optional[int] = None
    predicted_likes: Optional[int] = None
    predicted_shares: Optional[int] = None
    predicted_comments: Optional[int] = None
    viral_probability: Decimal = Field(max_digits=5, decimal_places=4)
    engagement_score: Decimal = Field(max_digits=5, decimal_places=4)
    model_version: str = Field(max_length=50)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EngagementPredictionCreate(EngagementPredictionBase):
    pass


class EngagementPredictionUpdate(SQLModel):
    predicted_views: Optional[int] = None
    predicted_likes: Optional[int] = None
    predicted_shares: Optional[int] = None
    predicted_comments: Optional[int] = None
    viral_probability: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    engagement_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    prediction_accuracy: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    extra_data: Optional[Dict[str, Any]] = None


class EngagementPrediction(EngagementPredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prediction_accuracy: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class EngagementPredictionPublic(EngagementPredictionBase):
    id: UUID
    prediction_accuracy: Optional[Decimal] = None
    created_at: datetime


# Churn Prediction Schemas
class ChurnPredictionBase(SQLModel):
    user_id: UUID
    churn_probability: Decimal = Field(max_digits=5, decimal_places=4)
    churn_risk_level: str = Field(max_length=20)
    predicted_churn_date: Optional[datetime] = None
    retention_recommendations: List[str] = Field(default_factory=list)
    model_version: str = Field(max_length=50)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChurnPredictionCreate(ChurnPredictionBase):
    pass


class ChurnPredictionUpdate(SQLModel):
    churn_probability: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    churn_risk_level: Optional[str] = Field(default=None, max_length=20)
    predicted_churn_date: Optional[datetime] = None
    retention_recommendations: Optional[List[str]] = None
    is_action_taken: Optional[bool] = None
    action_result: Optional[str] = Field(default=None, max_length=200)
    extra_data: Optional[Dict[str, Any]] = None


class ChurnPrediction(ChurnPredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_action_taken: bool
    action_result: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ChurnPredictionPublic(ChurnPredictionBase):
    id: UUID
    is_action_taken: bool
    action_result: Optional[str] = None
    created_at: datetime


# Translation Cache Schemas
class TranslationCacheBase(SQLModel):
    content_type: str = Field(max_length=50)
    content_id: UUID
    source_language: str = Field(max_length=10)
    target_language: str = Field(max_length=10)
    translated_text: str
    translation_quality: Optional[Decimal] = Field(
        default=None, max_digits=3, decimal_places=2
    )
    translation_service: str = Field(max_length=50)
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TranslationCacheCreate(TranslationCacheBase):
    pass


class TranslationCacheUpdate(SQLModel):
    translated_text: Optional[str] = None
    translation_quality: Optional[Decimal] = Field(
        default=None, max_digits=3, decimal_places=2
    )
    is_active: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TranslationCache(TranslationCacheBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class TranslationCachePublic(TranslationCacheBase):
    id: UUID
    is_active: bool
    created_at: datetime


# AI Model Metrics Schemas
class AIModelMetricsBase(SQLModel):
    model_name: str = Field(max_length=100)
    model_version: str = Field(max_length=50)
    metric_type: str = Field(max_length=50)
    metric_value: Decimal = Field(max_digits=8, decimal_places=6)
    dataset_size: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AIModelMetricsCreate(AIModelMetricsBase):
    pass


class AIModelMetricsUpdate(SQLModel):
    metric_value: Optional[Decimal] = Field(
        default=None, max_digits=8, decimal_places=6
    )
    dataset_size: Optional[int] = None
    is_baseline: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class AIModelMetrics(AIModelMetricsBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evaluation_date: datetime
    is_baseline: bool
    created_at: datetime


class AIModelMetricsPublic(AIModelMetricsBase):
    id: UUID
    evaluation_date: datetime
    is_baseline: bool
    created_at: datetime


# API Request/Response Schemas
class ContentAnalysisRequest(BaseModel):
    content_type: str
    content_id: UUID
    text: str
    analysis_types: List[str] = Field(
        default_factory=lambda: ["sentiment", "hashtags", "summary"]
    )
    include_metadata: bool = Field(default=True)


class ContentAnalysisResponse(BaseModel):
    content_id: UUID
    analysis_results: Dict[str, Any]
    processing_time_ms: int
    model_versions: Dict[str, str]


class RecommendationRequest(BaseModel):
    user_id: UUID
    content_types: List[str] = Field(
        default_factory=lambda: ["post", "news", "story", "reel"]
    )
    limit: int = Field(default=20, ge=1, le=100)
    exclude_viewed: bool = Field(default=True)


class RecommendationResponse(BaseModel):
    user_id: UUID
    recommendations: List[ContentRecommendationPublic]
    algorithm_version: str
    generated_at: datetime


class TranslationRequest(BaseModel):
    content_type: str
    content_id: UUID
    source_language: str
    target_language: str
    text: str


class TranslationResponse(BaseModel):
    content_id: UUID
    translated_text: str
    source_language: str
    target_language: str
    quality_score: Optional[float] = None
    cached: bool = False


class TrendAnalysisResponse(BaseModel):
    trends: List[TrendAnalysisPublic]
    time_window: str
    region: Optional[str] = None
    total_trends: int


class EngagementPredictionRequest(BaseModel):
    content_type: str
    content_id: UUID
    include_historical_data: bool = Field(default=False)


class EngagementPredictionResponse(BaseModel):
    content_id: UUID
    predictions: EngagementPredictionPublic
    confidence_intervals: Optional[Dict[str, Dict[str, float]]] = None


class ChurnAnalysisResponse(BaseModel):
    user_id: UUID
    churn_risk: ChurnPredictionPublic
    risk_factors: List[str]
    recommended_actions: List[str]


class AIModelHealthCheck(BaseModel):
    model_name: str
    model_version: str
    status: str  # healthy, degraded, offline
    last_evaluation: Optional[datetime] = None
    metrics: Dict[str, float]
    alerts: List[str] = Field(default_factory=list)


class BulkAnalysisRequest(BaseModel):
    content_items: List[ContentAnalysisRequest]
    priority: str = Field(default="normal")  # low, normal, high, urgent


class BulkAnalysisResponse(BaseModel):
    results: List[ContentAnalysisResponse]
    failed_items: List[Dict[str, Any]] = Field(default_factory=list)
    processing_stats: Dict[str, Any]
