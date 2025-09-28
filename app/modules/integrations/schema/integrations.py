from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import SQLModel


# Integration Schemas
class IntegrationBase(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    integration_type: str = Field(max_length=50)
    provider: str = Field(max_length=100)
    status: str = Field(default="pending")
    config: Dict[str, Any] = Field(default_factory=dict)
    credentials: Dict[str, Any] = Field(default_factory=dict)
    rate_limits: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IntegrationCreate(IntegrationBase):
    pass


class IntegrationUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    rate_limits: Optional[Dict[str, Any]] = None
    integration_metadata: Optional[Dict[str, Any]] = None


class Integration(IntegrationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    last_sync_at: Optional[datetime] = None
    error_count: int
    success_count: int


class IntegrationPublic(IntegrationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_sync_at: Optional[datetime] = None
    error_count: int
    success_count: int


# Webhook Schemas
class WebhookBase(BaseModel):
    url: str = Field(max_length=500)
    events: List[str] = Field(default_factory=list)
    secret: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    retry_count: int = Field(default=3)
    timeout_seconds: int = Field(default=30)
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)


class WebhookCreate(WebhookBase):
    integration_id: UUID


class WebhookUpdate(SQLModel):
    url: Optional[str] = Field(default=None, max_length=500)
    events: Optional[List[str]] = None
    secret: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None
    retry_count: Optional[int] = None
    timeout_seconds: Optional[int] = None
    headers: Optional[Dict[str, str]] = None


class Webhook(WebhookBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime] = None
    failure_count: int
    success_count: int


class WebhookPublic(WebhookBase):
    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime] = None
    failure_count: int
    success_count: int


# API Key Schemas
class APIKeyBase(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    permissions: List[str] = Field(default_factory=list)
    rate_limit: int = Field(default=1000)
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    integration_id: UUID


class APIKeyUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    permissions: Optional[List[str]] = None
    rate_limit: Optional[int] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class APIKey(APIKeyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    usage_count: int


class APIKeyPublic(APIKeyBase):
    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    usage_count: int


# Social Media Integration Schemas
class SocialMediaPostBase(BaseModel):
    platform: str = Field(max_length=50)
    external_id: str = Field(max_length=255)
    content_type: str = Field(max_length=50)
    content_id: UUID
    post_url: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(default="pending")
    posted_at: Optional[datetime] = None
    engagement_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SocialMediaPostCreate(SocialMediaPostBase):
    integration_id: UUID


class SocialMediaPostUpdate(SQLModel):
    post_url: Optional[str] = Field(default=None, max_length=500)
    status: Optional[str] = None
    posted_at: Optional[datetime] = None
    engagement_data: Optional[Dict[str, Any]] = None


class SocialMediaPost(SocialMediaPostBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class SocialMediaPostPublic(SocialMediaPostBase):
    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


# News API Integration Schemas
class NewsSourceBase(BaseModel):
    name: str = Field(max_length=200)
    external_id: str = Field(max_length=255)
    url: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(default=None, max_length=100)
    language: str = Field(default="en", max_length=10)
    country: Optional[str] = Field(default=None, max_length=10)
    credibility_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )
    is_active: bool = Field(default=True)


class NewsSourceCreate(NewsSourceBase):
    integration_id: UUID


class NewsSourceUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=200)
    url: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, max_length=10)
    country: Optional[str] = Field(default=None, max_length=10)
    credibility_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )
    is_active: Optional[bool] = None


class NewsSource(NewsSourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_fetched_at: Optional[datetime] = None
    article_count: int


class NewsSourcePublic(NewsSourceBase):
    id: UUID
    integration_id: UUID
    created_at: datetime
    updated_at: datetime
    last_fetched_at: Optional[datetime] = None
    article_count: int


class ExternalNewsArticleBase(BaseModel):
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    content: Optional[str] = Field(default=None)
    url: str = Field(max_length=500)
    external_id: str = Field(max_length=255)
    published_at: datetime
    author: Optional[str] = Field(default=None, max_length=200)
    image_url: Optional[str] = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    sentiment_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )


class ExternalNewsArticleCreate(ExternalNewsArticleBase):
    source_id: UUID
    integration_id: UUID


class ExternalNewsArticleUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    content: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None, max_length=200)
    image_url: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[List[str]] = None
    sentiment_score: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )
    imported_at: Optional[datetime] = None
    is_imported: Optional[bool] = None


class ExternalNewsArticle(ExternalNewsArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    integration_id: UUID
    created_at: datetime
    imported_at: Optional[datetime] = None
    is_imported: bool


class ExternalNewsArticlePublic(ExternalNewsArticleBase):
    id: UUID
    source_id: UUID
    integration_id: UUID
    created_at: datetime
    imported_at: Optional[datetime] = None
    is_imported: bool


# Webhook Delivery Schemas
class WebhookDeliveryBase(BaseModel):
    event: str = Field(max_length=100)
    payload: Dict[str, Any] = Field(default_factory=dict)
    response_status: Optional[int] = None
    response_body: Optional[str] = Field(default=None, max_length=10000)
    attempt_count: int = Field(default=1)
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = Field(default=None, max_length=1000)


class WebhookDeliveryCreate(WebhookDeliveryBase):
    webhook_id: UUID


class WebhookDeliveryUpdate(SQLModel):
    response_status: Optional[int] = None
    response_body: Optional[str] = Field(default=None, max_length=10000)
    attempt_count: Optional[int] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = Field(default=None, max_length=1000)


class WebhookDelivery(WebhookDeliveryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    webhook_id: UUID
    created_at: datetime


class WebhookDeliveryPublic(WebhookDeliveryBase):
    id: UUID
    webhook_id: UUID
    created_at: datetime


# API Request Log Schemas
class APIRequestLogBase(BaseModel):
    method: str = Field(max_length=10)
    endpoint: str = Field(max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    response_status: int
    response_time_ms: int
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    error_message: Optional[str] = Field(default=None, max_length=1000)


class APIRequestLogCreate(APIRequestLogBase):
    api_key_id: UUID


class APIRequestLog(APIRequestLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    api_key_id: UUID
    created_at: datetime


class APIRequestLogPublic(APIRequestLogBase):
    id: UUID
    api_key_id: UUID
    created_at: datetime


# Integration Sync Log Schemas
class IntegrationSyncLogBase(BaseModel):
    operation: str = Field(max_length=100)
    status: str = Field(max_length=50)
    records_processed: int = Field(default=0)
    records_failed: int = Field(default=0)
    duration_ms: Optional[int] = None
    error_message: Optional[str] = Field(default=None, max_length=2000)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IntegrationSyncLogCreate(IntegrationSyncLogBase):
    integration_id: UUID


class IntegrationSyncLog(IntegrationSyncLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    created_at: datetime


class IntegrationSyncLogPublic(IntegrationSyncLogBase):
    id: UUID
    integration_id: UUID
    created_at: datetime


# Third-party Service Data Schemas
class WeatherDataBase(BaseModel):
    location: str = Field(max_length=200)
    temperature_celsius: Decimal = Field(max_digits=5, decimal_places=2)
    temperature_fahrenheit: Decimal = Field(max_digits=5, decimal_places=2)
    humidity_percent: int
    wind_speed_kmh: Decimal = Field(max_digits=5, decimal_places=2)
    wind_speed_mph: Decimal = Field(max_digits=5, decimal_places=2)
    condition: str = Field(max_length=100)
    icon_url: Optional[str] = Field(default=None, max_length=500)
    forecast_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WeatherDataCreate(WeatherDataBase):
    integration_id: UUID
    expires_at: datetime


class WeatherDataUpdate(SQLModel):
    temperature_celsius: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )
    temperature_fahrenheit: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )
    humidity_percent: Optional[int] = None
    wind_speed_kmh: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )
    wind_speed_mph: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )
    condition: Optional[str] = Field(default=None, max_length=100)
    icon_url: Optional[str] = Field(default=None, max_length=500)
    forecast_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class WeatherData(WeatherDataBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime


class WeatherDataPublic(WeatherDataBase):
    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime


class StockDataBase(BaseModel):
    symbol: str = Field(max_length=20)
    company_name: str = Field(max_length=200)
    current_price: Decimal = Field(max_digits=15, decimal_places=4)
    change_amount: Decimal = Field(max_digits=15, decimal_places=4)
    change_percent: Decimal = Field(max_digits=7, decimal_places=4)
    volume: int
    market_cap: Optional[Decimal] = Field(default=None, max_digits=20, decimal_places=2)
    pe_ratio: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    historical_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class StockDataCreate(StockDataBase):
    integration_id: UUID
    expires_at: datetime


class StockDataUpdate(SQLModel):
    current_price: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=4
    )
    change_amount: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=4
    )
    change_percent: Optional[Decimal] = Field(
        default=None, max_digits=7, decimal_places=4
    )
    volume: Optional[int] = None
    market_cap: Optional[Decimal] = Field(default=None, max_digits=20, decimal_places=2)
    pe_ratio: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    historical_data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class StockData(StockDataBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime


class StockDataPublic(StockDataBase):
    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime


class SportsDataBase(BaseModel):
    league: str = Field(max_length=100)
    sport: str = Field(max_length=50)
    event_type: str = Field(max_length=50)
    event_name: str = Field(max_length=200)
    external_id: str = Field(max_length=255)
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = Field(max_length=50)
    venue: Optional[str] = Field(default=None, max_length=200)
    participants: List[Dict[str, Any]] = Field(default_factory=list)
    scores: Optional[Dict[str, Any]] = Field(default_factory=dict)
    live_stats: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SportsDataCreate(SportsDataBase):
    integration_id: UUID
    expires_at: datetime


class SportsDataUpdate(SQLModel):
    end_time: Optional[datetime] = None
    status: Optional[str] = Field(default=None, max_length=50)
    venue: Optional[str] = Field(default=None, max_length=200)
    participants: Optional[List[Dict[str, Any]]] = None
    scores: Optional[Dict[str, Any]] = None
    live_stats: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class SportsData(SportsDataBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime


class SportsDataPublic(SportsDataBase):
    id: UUID
    integration_id: UUID
    fetched_at: datetime
    expires_at: datetime


# Request/Response Schemas for API Endpoints
class IntegrationTestRequest(BaseModel):
    test_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IntegrationTestResponse(BaseModel):
    success: bool
    message: str
    response_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None


class WebhookTriggerRequest(BaseModel):
    event: str
    payload: Dict[str, Any]


class WebhookTriggerResponse(BaseModel):
    success: bool
    webhook_id: UUID
    delivery_id: Optional[UUID] = None
    message: str


class SocialMediaPostRequest(BaseModel):
    platform: str
    content_type: str
    content_id: UUID
    message: Optional[str] = None
    media_urls: Optional[List[str]] = None


class SocialMediaPostResponse(BaseModel):
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    message: str
    error_details: Optional[Dict[str, Any]] = None


class NewsFetchRequest(BaseModel):
    source_ids: Optional[List[UUID]] = None
    categories: Optional[List[str]] = None
    limit: int = Field(default=50, ge=1, le=200)
    language: Optional[str] = None


class NewsFetchResponse(BaseModel):
    success: bool
    articles_fetched: int
    sources_updated: int
    message: str
    articles: Optional[List[ExternalNewsArticlePublic]] = None


class WeatherRequest(BaseModel):
    location: str
    include_forecast: bool = Field(default=False)


class WeatherResponse(BaseModel):
    success: bool
    data: Optional[WeatherDataPublic] = None
    message: str
    error_details: Optional[Dict[str, Any]] = None


class StockRequest(BaseModel):
    symbols: List[str]
    include_history: bool = Field(default=False)


class StockResponse(BaseModel):
    success: bool
    data: Optional[List[StockDataPublic]] = None
    message: str
    error_details: Optional[Dict[str, Any]] = None


class SportsRequest(BaseModel):
    sport: Optional[str] = None
    league: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)


class SportsResponse(BaseModel):
    success: bool
    data: Optional[List[SportsDataPublic]] = None
    message: str
    error_details: Optional[Dict[str, Any]] = None


class IntegrationSyncRequest(BaseModel):
    integration_id: UUID
    operation: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IntegrationSyncResponse(BaseModel):
    success: bool
    sync_log_id: Optional[UUID] = None
    records_processed: int = Field(default=0)
    records_failed: int = Field(default=0)
    message: str
    error_details: Optional[Dict[str, Any]] = None


class APIKeyGenerateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    rate_limit: int = Field(default=1000)
    expires_at: Optional[datetime] = None


class APIKeyGenerateResponse(BaseModel):
    success: bool
    api_key: Optional[APIKeyPublic] = None
    raw_key: Optional[str] = None
    message: str


class IntegrationStatsResponse(BaseModel):
    total_integrations: int
    active_integrations: int
    integrations_by_type: Dict[str, int]
    integrations_by_status: Dict[str, int]
    recent_syncs: List[IntegrationSyncLogPublic]
    webhook_deliveries_today: int
    api_requests_today: int


class WebhookStatsResponse(BaseModel):
    total_webhooks: int
    active_webhooks: int
    total_deliveries: int
    success_rate: float
    recent_deliveries: List[WebhookDeliveryPublic]


class APIKeyStatsResponse(BaseModel):
    total_keys: int
    active_keys: int
    total_requests: int
    average_response_time: float
    top_endpoints: List[Dict[str, Any]]
    recent_requests: List[APIRequestLogPublic]
