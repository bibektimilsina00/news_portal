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


class ContentRecommendation(SQLModel, table=True):
    """AI-generated content recommendations for users."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    content_type: str = Field(max_length=50)  # post, news, story, reel
    content_id: UUID = Field(index=True)
    recommendation_score: Decimal = Field(
        max_digits=5, decimal_places=4
    )  # 0.0000 to 1.0000
    recommendation_reason: str = Field(
        max_length=100
    )  # trending, similar_interests, etc.
    algorithm_version: str = Field(max_length=50)
    is_viewed: bool = Field(default=False)
    is_clicked: bool = Field(default=False)
    position: Optional[int] = Field(default=None)  # Position in recommendation feed
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="content_recommendations")


class ContentAnalysis(SQLModel, table=True):
    """AI analysis results for content."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    content_type: str = Field(max_length=50)
    content_id: UUID = Field(index=True)
    analysis_type: str = Field(max_length=50)  # sentiment, hashtags, summary, etc.
    analysis_result: dict = Field(
        sa_column=Column(JSON)
    )  # Store analysis results as JSON
    confidence_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    model_version: str = Field(max_length=50)
    processing_time_ms: Optional[int] = Field(default=None)
    is_active: bool = Field(default=True)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class UserBehavior(SQLModel, table=True):
    """User behavior tracking for ML models."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    action_type: str = Field(max_length=50)  # view, like, share, comment, follow, etc.
    target_type: str = Field(max_length=50)  # post, news, user, story, reel
    target_id: UUID = Field(index=True)
    session_id: Optional[UUID] = Field(default=None, max_length=100)
    device_info: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    location_info: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    duration_seconds: Optional[int] = Field(default=None)  # For views
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="behavior_logs")


class PersonalizedFeed(SQLModel, table=True):
    """Personalized feed configurations for users."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, unique=True)
    feed_algorithm: str = Field(default="collaborative_filtering", max_length=50)
    content_categories: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_sources: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    excluded_topics: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    language_preferences: List[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    time_preferences: Optional[dict] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    is_active: bool = Field(default=True)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="personalized_feed")


class TrendAnalysis(SQLModel, table=True):
    """Trend analysis and predictions."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    trend_type: str = Field(max_length=50)  # hashtag, topic, content_type, etc.
    trend_value: str = Field(max_length=200)
    trend_score: Decimal = Field(max_digits=8, decimal_places=4)
    growth_rate: Decimal = Field(max_digits=6, decimal_places=4)  # Percentage growth
    prediction_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    time_window: str = Field(max_length=20)  # 1h, 24h, 7d, 30d
    region: Optional[str] = Field(default=None, max_length=10)  # Country code
    language: Optional[str] = Field(default=None, max_length=10)
    is_viral: bool = Field(default=False)
    peak_time: Optional[datetime] = None
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class ContentClassification(SQLModel, table=True):
    """Content classification results."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    content_type: str = Field(max_length=50)
    content_id: UUID = Field(index=True)
    category: str = Field(max_length=100)
    subcategory: Optional[str] = Field(default=None, max_length=100)
    confidence_score: Decimal = Field(max_digits=5, decimal_places=4)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    keywords: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    sentiment_score: Optional[Decimal] = Field(
        default=None, max_digits=3, decimal_places=2
    )  # -1.0 to 1.0
    toxicity_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    model_version: str = Field(max_length=50)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class AnomalyDetection(SQLModel, table=True):
    """Anomaly detection results."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    target_type: str = Field(max_length=50)  # user, content, behavior, etc.
    target_id: UUID = Field(index=True)
    anomaly_type: str = Field(max_length=50)  # bot_activity, spam, fraud, etc.
    anomaly_score: Decimal = Field(max_digits=5, decimal_places=4)
    threshold_breached: Decimal = Field(max_digits=5, decimal_places=4)
    detection_method: str = Field(max_length=50)
    is_investigated: bool = Field(default=False)
    investigation_result: Optional[str] = Field(default=None, max_length=200)
    false_positive: Optional[bool] = Field(default=None)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class EngagementPrediction(SQLModel, table=True):
    """Engagement predictions for content."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    content_type: str = Field(max_length=50)
    content_id: UUID = Field(index=True)
    predicted_views: Optional[int] = Field(default=None)
    predicted_likes: Optional[int] = Field(default=None)
    predicted_shares: Optional[int] = Field(default=None)
    predicted_comments: Optional[int] = Field(default=None)
    viral_probability: Decimal = Field(max_digits=5, decimal_places=4)
    engagement_score: Decimal = Field(max_digits=5, decimal_places=4)
    model_version: str = Field(max_length=50)
    prediction_accuracy: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=4
    )
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class ChurnPrediction(SQLModel, table=True):
    """User churn predictions."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    churn_probability: Decimal = Field(max_digits=5, decimal_places=4)
    churn_risk_level: str = Field(max_length=20)  # low, medium, high, critical
    predicted_churn_date: Optional[datetime] = None
    retention_recommendations: List[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    model_version: str = Field(max_length=50)
    is_action_taken: bool = Field(default=False)
    action_result: Optional[str] = Field(default=None, max_length=200)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="churn_predictions")


class TranslationCache(SQLModel, table=True):
    """Cache for translated content."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    content_type: str = Field(max_length=50)
    content_id: UUID = Field(index=True)
    source_language: str = Field(max_length=10)
    target_language: str = Field(max_length=10)
    translated_text: str
    translation_quality: Optional[Decimal] = Field(
        default=None, max_digits=3, decimal_places=2
    )
    translation_service: str = Field(max_length=50)
    is_active: bool = Field(default=True)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class AIModelMetrics(SQLModel, table=True):
    """Performance metrics for AI models."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    model_name: str = Field(max_length=100)
    model_version: str = Field(max_length=50)
    metric_type: str = Field(
        max_length=50
    )  # accuracy, precision, recall, f1_score, etc.
    metric_value: Decimal = Field(max_digits=8, decimal_places=6)
    dataset_size: Optional[int] = Field(default=None)
    evaluation_date: datetime = Field(default_factory=datetime.utcnow)
    is_baseline: bool = Field(default=False)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
