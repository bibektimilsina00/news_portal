import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import String
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.shared.enums import IntegrationStatus, IntegrationType, WebhookEvent


# Core Integration Models
class IntegrationBase(SQLModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    integration_type: str = Field(max_length=50)
    provider: str = Field(max_length=100)  # e.g., "twitter", "openweather", "stripe"
    status: str = Field(default="pending")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    credentials: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    rate_limits: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    integration_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class Integration(IntegrationBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync_at: Optional[datetime] = None
    error_count: int = Field(default=0)
    success_count: int = Field(default=0)

    # Relationships
    webhooks: List["Webhook"] = Relationship(back_populates="integration")
    api_keys: List["APIKey"] = Relationship(back_populates="integration")
    sync_logs: List["IntegrationSyncLog"] = Relationship(back_populates="integration")


class IntegrationPublic(IntegrationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_sync_at: Optional[datetime] = None
    error_count: int
    success_count: int


# Webhook Models
class WebhookBase(SQLModel):
    url: str = Field(max_length=500)
    events: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    secret: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    retry_count: int = Field(default=3)
    timeout_seconds: int = Field(default=30)
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class Webhook(WebhookBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    integration_id: UUID = Field(foreign_key="integration.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_triggered_at: Optional[datetime] = None
    failure_count: int = Field(default=0)
    success_count: int = Field(default=0)

    # Relationships
    integration: Integration = Relationship(back_populates="webhooks")
    deliveries: List["WebhookDelivery"] = Relationship(back_populates="webhook")


class WebhookPublic(WebhookBase):
    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime] = None
    failure_count: int
    success_count: int


# API Key Models
class APIKeyBase(SQLModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    key_hash: str = Field(max_length=255, unique=True)
    permissions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    rate_limit: int = Field(default=1000)  # requests per hour
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = None


class APIKey(APIKeyBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    integration_id: UUID = Field(foreign_key="integration.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None
    usage_count: int = Field(default=0)

    # Relationships
    integration: Integration = Relationship(back_populates="api_keys")
    requests: List["APIRequestLog"] = Relationship(back_populates="api_key")


class APIKeyPublic(APIKeyBase):
    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    usage_count: int


# Social Media Integration Models
class SocialMediaPostBase(SQLModel):
    platform: str = Field(max_length=50)  # twitter, facebook, instagram, linkedin
    external_id: UUID = Field(default_factory=uuid.uuid4, max_length=255)
    content_type: str = Field(max_length=50)  # post, story, reel, etc.
    content_id: UUID  # Reference to our internal content
    post_url: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(default="pending")  # pending, posted, failed
    posted_at: Optional[datetime] = None
    engagement_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class SocialMediaPost(SocialMediaPostBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    integration_id: UUID = Field(foreign_key="integration.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = Field(default=None, max_length=1000)

    # Relationships
    integration: Integration = Relationship()


class SocialMediaPostPublic(SocialMediaPostBase):
    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


# News API Integration Models
class NewsSourceBase(SQLModel):
    name: str = Field(max_length=200)
    external_id: UUID = Field(default_factory=uuid.uuid4, max_length=255, unique=True)
    url: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(default=None, max_length=100)
    language: str = Field(default="en", max_length=10)
    country: Optional[str] = Field(default=None, max_length=10)
    credibility_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )
    is_active: bool = Field(default=True)


class IntegrationNewsSource(NewsSourceBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    integration_id: UUID = Field(foreign_key="integration.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_fetched_at: Optional[datetime] = None
    article_count: int = Field(default=0)

    # Relationships
    integration: Integration = Relationship()
    articles: List["ExternalNewsArticle"] = Relationship(back_populates="source")


class NewsSourcePublic(NewsSourceBase):
    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_fetched_at: Optional[datetime] = None
    article_count: int


class ExternalNewsArticleBase(SQLModel):
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    content: Optional[str] = Field(default=None)
    url: str = Field(max_length=500)
    external_id: UUID = Field(default_factory=uuid.uuid4, max_length=255, unique=True)
    published_at: datetime
    author: Optional[str] = Field(default=None, max_length=200)
    image_url: Optional[str] = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    sentiment_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )


class ExternalNewsArticle(ExternalNewsArticleBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source_id: UUID = Field(foreign_key="integrationnewssource.id")
    integration_id: UUID = Field(foreign_key="integration.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    imported_at: Optional[datetime] = None
    is_imported: bool = Field(default=False)

    # Relationships
    source: IntegrationNewsSource = Relationship(back_populates="articles")
    integration: Integration = Relationship()


class ExternalNewsArticlePublic(ExternalNewsArticleBase):
    id: UUID
    source_id: UUID
    integration_id: UUID
    created_at: datetime
    imported_at: Optional[datetime] = None
    is_imported: bool


# Webhook Delivery Models
class WebhookDeliveryBase(SQLModel):
    event: str = Field(max_length=100)
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    response_status: Optional[int] = None
    response_body: Optional[str] = Field(default=None, max_length=10000)
    attempt_count: int = Field(default=1)
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = Field(default=None, max_length=1000)


class WebhookDelivery(WebhookDeliveryBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    webhook_id: UUID = Field(foreign_key="webhook.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    webhook: Webhook = Relationship(back_populates="deliveries")


class WebhookDeliveryPublic(WebhookDeliveryBase):
    id: UUID
    webhook_id: UUID
    created_at: datetime


# API Request Log Models
class APIRequestLogBase(SQLModel):
    method: str = Field(max_length=10)
    endpoint: str = Field(max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    response_status: int
    response_time_ms: int
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    error_message: Optional[str] = Field(default=None, max_length=1000)


class APIRequestLog(APIRequestLogBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    api_key_id: UUID = Field(foreign_key="apikey.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    api_key: APIKey = Relationship(back_populates="requests")


class APIRequestLogPublic(APIRequestLogBase):
    id: UUID
    api_key_id: UUID
    created_at: datetime


# Integration Sync Log Models
class IntegrationSyncLogBase(SQLModel):
    operation: str = Field(max_length=100)
    status: str = Field(max_length=50)  # success, error, partial
    records_processed: int = Field(default=0)
    records_failed: int = Field(default=0)
    duration_ms: Optional[int] = None
    error_message: Optional[str] = Field(default=None, max_length=2000)
    sync_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class IntegrationSyncLog(IntegrationSyncLogBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    integration_id: UUID = Field(foreign_key="integration.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    integration: Integration = Relationship(back_populates="sync_logs")


class IntegrationSyncLogPublic(IntegrationSyncLogBase):
    id: UUID
    integration_id: UUID
    created_at: datetime


# Third-party Service Data Models
class WeatherDataBase(SQLModel):
    location: str = Field(max_length=200)
    temperature_celsius: Decimal = Field(max_digits=5, decimal_places=2)
    temperature_fahrenheit: Decimal = Field(max_digits=5, decimal_places=2)
    humidity_percent: int
    wind_speed_kmh: Decimal = Field(max_digits=5, decimal_places=2)
    wind_speed_mph: Decimal = Field(max_digits=5, decimal_places=2)
    condition: str = Field(max_length=100)
    icon_url: Optional[str] = Field(default=None, max_length=500)
    forecast_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class WeatherData(WeatherDataBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    integration_id: UUID = Field(foreign_key="integration.id")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    # Relationships
    integration: Integration = Relationship()


class WeatherDataPublic(WeatherDataBase):
    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime


class StockDataBase(SQLModel):
    symbol: str = Field(max_length=20, unique=True)
    company_name: str = Field(max_length=200)
    current_price: Decimal = Field(max_digits=15, decimal_places=4)
    change_amount: Decimal = Field(max_digits=15, decimal_places=4)
    change_percent: Decimal = Field(max_digits=7, decimal_places=4)
    volume: int
    market_cap: Optional[Decimal] = Field(default=None, max_digits=20, decimal_places=2)
    pe_ratio: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    historical_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class StockData(StockDataBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    integration_id: UUID = Field(foreign_key="integration.id")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    # Relationships
    integration: Integration = Relationship()


class StockDataPublic(StockDataBase):
    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime


class SportsDataBase(SQLModel):
    league: str = Field(max_length=100)
    sport: str = Field(max_length=50)
    event_type: str = Field(max_length=50)  # match, tournament, season
    event_name: str = Field(max_length=200)
    external_id: UUID = Field(default_factory=uuid.uuid4, max_length=255)
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = Field(max_length=50)  # scheduled, live, finished, cancelled
    venue: Optional[str] = Field(default=None, max_length=200)
    participants: List[Dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    scores: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    live_stats: Optional[Dict[str, Any]] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class SportsData(SportsDataBase, table=True):

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    integration_id: UUID = Field(foreign_key="integration.id")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    # Relationships
    integration: Integration = Relationship()


class SportsDataPublic(SportsDataBase):
    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime
