from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.modules.integrations.schema.integrations import (
    APIKeyCreate,
    APIKeyGenerateRequest,
    APIKeyGenerateResponse,
    APIKeyPublic,
    APIKeyStatsResponse,
    APIKeyUpdate,
    APIRequestLogPublic,
    ExternalNewsArticlePublic,
    IntegrationCreate,
    IntegrationPublic,
    IntegrationStatsResponse,
    IntegrationSyncLogPublic,
    IntegrationSyncRequest,
    IntegrationSyncResponse,
    IntegrationTestRequest,
    IntegrationTestResponse,
    IntegrationUpdate,
    NewsFetchRequest,
    NewsFetchResponse,
    NewsSourcePublic,
    SocialMediaPostPublic,
    SocialMediaPostRequest,
    SocialMediaPostResponse,
    SportsDataPublic,
    SportsRequest,
    SportsResponse,
    StockDataPublic,
    StockRequest,
    StockResponse,
    WeatherDataPublic,
    WeatherRequest,
    WeatherResponse,
    WebhookCreate,
    WebhookDeliveryPublic,
    WebhookPublic,
    WebhookStatsResponse,
    WebhookTriggerRequest,
    WebhookTriggerResponse,
    WebhookUpdate,
)
from app.modules.integrations.services.integrations_service import IntegrationsService
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter()


# Integration Management Endpoints
@router.post("/", response_model=IntegrationPublic)
def create_integration(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_data: IntegrationCreate,
) -> IntegrationPublic:
    """Create a new integration."""
    service = IntegrationsService(session)
    return service.create_integration(integration_data)


@router.get("/", response_model=List[IntegrationPublic])
def get_integrations(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[IntegrationPublic]:
    """Get all integrations."""
    service = IntegrationsService(session)
    return service.get_integrations(skip=skip, limit=limit)


@router.get("/{integration_id}", response_model=IntegrationPublic)
def get_integration(
    *, session: SessionDep, current_user: CurrentUser, integration_id: UUID
) -> IntegrationPublic:
    """Get integration by ID."""
    service = IntegrationsService(session)
    integration = service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.put("/{integration_id}", response_model=IntegrationPublic)
def update_integration(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: UUID,
    integration_data: IntegrationUpdate,
) -> IntegrationPublic:
    """Update integration."""
    service = IntegrationsService(session)
    return service.update_integration(integration_id, integration_data)


@router.delete("/{integration_id}", response_model=Message)
def delete_integration(
    *, session: SessionDep, current_user: CurrentUser, integration_id: UUID
) -> Message:
    """Delete integration."""
    service = IntegrationsService(session)
    return service.delete_integration(integration_id)


@router.post("/{integration_id}/test", response_model=IntegrationTestResponse)
async def test_integration(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: UUID,
    test_request: IntegrationTestRequest = None,
) -> IntegrationTestResponse:
    """Test integration connectivity."""
    if test_request is None:
        test_request = IntegrationTestRequest()
    service = IntegrationsService(session)
    return await service.test_integration(integration_id, test_request)


@router.post("/{integration_id}/sync", response_model=IntegrationSyncResponse)
async def sync_integration(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: UUID,
    sync_request: IntegrationSyncRequest,
) -> IntegrationSyncResponse:
    """Sync integration data."""
    service = IntegrationsService(session)
    return await service.sync_integration(sync_request)


# Webhook Management Endpoints
@router.post("/webhooks/", response_model=WebhookPublic)
def create_webhook(
    *, session: SessionDep, current_user: CurrentUser, webhook_data: WebhookCreate
) -> WebhookPublic:
    """Create a new webhook."""
    service = IntegrationsService(session)
    return service.create_webhook(webhook_data)


@router.get("/webhooks/", response_model=List[WebhookPublic])
def get_webhooks(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: Optional[UUID] = Query(
        None, description="Filter by integration ID"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[WebhookPublic]:
    """Get all webhooks."""
    from app.modules.integrations.crud.integrations_crud import crud_webhook

    if integration_id:
        return crud_webhook.get_by_integration(session, integration_id)
    return crud_webhook.get_multi(session, skip=skip, limit=limit)


@router.get("/webhooks/{webhook_id}", response_model=WebhookPublic)
def get_webhook(
    *, session: SessionDep, current_user: CurrentUser, webhook_id: UUID
) -> WebhookPublic:
    """Get webhook by ID."""
    service = IntegrationsService(session)
    webhook = service.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.put("/webhooks/{webhook_id}", response_model=WebhookPublic)
def update_webhook(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    webhook_id: UUID,
    webhook_data: WebhookUpdate,
) -> WebhookPublic:
    """Update webhook."""
    service = IntegrationsService(session)
    return service.update_webhook(webhook_id, webhook_data)


@router.delete("/webhooks/{webhook_id}", response_model=Message)
def delete_webhook(
    *, session: SessionDep, current_user: CurrentUser, webhook_id: UUID
) -> Message:
    """Delete webhook."""
    service = IntegrationsService(session)
    return service.delete_webhook(webhook_id)


@router.post("/webhooks/{webhook_id}/trigger", response_model=WebhookTriggerResponse)
async def trigger_webhook(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    webhook_id: UUID,
    trigger_request: WebhookTriggerRequest,
) -> WebhookTriggerResponse:
    """Manually trigger a webhook."""
    service = IntegrationsService(session)
    return await service.trigger_webhook(webhook_id, trigger_request)


@router.get(
    "/webhooks/{webhook_id}/deliveries", response_model=List[WebhookDeliveryPublic]
)
def get_webhook_deliveries(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    webhook_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> List[WebhookDeliveryPublic]:
    """Get webhook delivery history."""
    from app.modules.integrations.crud.integrations_crud import crud_webhook_delivery

    return crud_webhook_delivery.get_by_webhook(session, webhook_id, limit)


# API Key Management Endpoints
@router.post("/api-keys/generate", response_model=APIKeyGenerateResponse)
def generate_api_key(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    key_request: APIKeyGenerateRequest,
) -> APIKeyGenerateResponse:
    """Generate a new API key."""
    service = IntegrationsService(session)
    return service.generate_api_key(key_request)


@router.get("/api-keys/", response_model=List[APIKeyPublic])
def get_api_keys(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: Optional[UUID] = Query(
        None, description="Filter by integration ID"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[APIKeyPublic]:
    """Get all API keys."""
    service = IntegrationsService(session)
    if integration_id:
        return service.get_api_keys_by_integration(integration_id)
    from app.modules.integrations.crud.integrations_crud import crud_api_key

    return crud_api_key.get_multi(session, skip=skip, limit=limit)


@router.delete("/api-keys/{api_key_id}", response_model=Message)
def revoke_api_key(
    *, session: SessionDep, current_user: CurrentUser, api_key_id: UUID
) -> Message:
    """Revoke an API key."""
    service = IntegrationsService(session)
    return service.revoke_api_key(api_key_id)


@router.get("/api-keys/{api_key_id}/requests", response_model=List[APIRequestLogPublic])
def get_api_key_requests(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    api_key_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[APIRequestLogPublic]:
    """Get API request logs for a key."""
    from app.modules.integrations.crud.integrations_crud import crud_api_request_log

    return crud_api_request_log.get_by_key(session, api_key_id, limit)


# Social Media Integration Endpoints
@router.post(
    "/{integration_id}/social-media/post", response_model=SocialMediaPostResponse
)
async def post_to_social_media(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: UUID,
    post_request: SocialMediaPostRequest,
) -> SocialMediaPostResponse:
    """Post content to social media platforms."""
    service = IntegrationsService(session)
    return await service.post_to_social_media(integration_id, post_request)


@router.get("/social-media/posts", response_model=List[SocialMediaPostPublic])
def get_social_media_posts(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: Optional[UUID] = Query(None),
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[SocialMediaPostPublic]:
    """Get social media posts."""
    from app.modules.integrations.crud.integrations_crud import crud_social_media_post

    # Simple filtering - in production, you might want more complex queries
    posts = crud_social_media_post.get_multi(session, skip=skip, limit=limit)

    # Apply filters
    if integration_id:
        posts = [p for p in posts if p.integration_id == integration_id]
    if platform:
        posts = [p for p in posts if p.platform == platform]
    if status:
        posts = [p for p in posts if p.status == status]

    return [SocialMediaPostPublic.model_validate(post) for post in posts]


# News API Integration Endpoints
@router.post("/{integration_id}/news/fetch", response_model=NewsFetchResponse)
async def fetch_news(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: UUID,
    fetch_request: NewsFetchRequest,
) -> NewsFetchResponse:
    """Fetch news from external APIs."""
    service = IntegrationsService(session)
    return await service.fetch_news(integration_id, fetch_request)


@router.get("/news/sources", response_model=List[NewsSourcePublic])
def get_news_sources(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: Optional[UUID] = Query(None),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[NewsSourcePublic]:
    """Get news sources."""
    from app.modules.integrations.crud.integrations_crud import crud_news_source

    if integration_id:
        sources = crud_news_source.get_active_by_integration(session, integration_id)
    else:
        sources = crud_news_source.get_multi(session, skip=skip, limit=limit)

    # Apply additional filters
    if category:
        sources = [s for s in sources if s.category == category]
    if is_active is not None:
        sources = [s for s in sources if s.is_active == is_active]

    return [NewsSourcePublic.model_validate(source) for source in sources[:limit]]


@router.get("/news/articles", response_model=List[ExternalNewsArticlePublic])
def get_news_articles(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    source_id: Optional[UUID] = Query(None),
    category: Optional[str] = Query(None),
    imported_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> List[ExternalNewsArticlePublic]:
    """Get external news articles."""
    from app.modules.integrations.crud.integrations_crud import (
        crud_external_news_article,
    )

    if source_id:
        articles = crud_external_news_article.get_by_source(session, source_id, limit)
    elif category:
        articles = crud_external_news_article.get_recent_by_category(
            session, category, limit
        )
    else:
        articles = crud_external_news_article.get_multi(session, skip=skip, limit=limit)

    if imported_only:
        articles = [a for a in articles if a.is_imported]

    return [ExternalNewsArticlePublic.model_validate(article) for article in articles]


@router.post("/news/articles/{article_id}/import", response_model=Message)
def import_news_article(
    *, session: SessionDep, current_user: CurrentUser, article_id: UUID
) -> Message:
    """Mark a news article as imported."""
    from app.modules.integrations.crud.integrations_crud import (
        crud_external_news_article,
    )

    crud_external_news_article.mark_imported(session, article_id)
    return Message(message="Article marked as imported")


# Third-party Service Endpoints
@router.post("/{integration_id}/weather", response_model=WeatherResponse)
async def get_weather(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: UUID,
    weather_request: WeatherRequest,
) -> WeatherResponse:
    """Get weather data."""
    service = IntegrationsService(session)
    return await service.get_weather(integration_id, weather_request)


@router.post("/{integration_id}/stocks", response_model=StockResponse)
async def get_stock_data(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: UUID,
    stock_request: StockRequest,
) -> StockResponse:
    """Get stock market data."""
    service = IntegrationsService(session)
    return await service.get_stock_data(integration_id, stock_request)


@router.post("/{integration_id}/sports", response_model=SportsResponse)
async def get_sports_data(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: UUID,
    sports_request: SportsRequest,
) -> SportsResponse:
    """Get sports data."""
    service = IntegrationsService(session)
    return await service.get_sports_data(integration_id, sports_request)


@router.get("/weather/cache", response_model=List[WeatherDataPublic])
def get_weather_cache(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    location: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[WeatherDataPublic]:
    """Get cached weather data."""
    from app.modules.integrations.crud.integrations_crud import crud_weather_data

    if location:
        data = crud_weather_data.get_current_by_location(session, location)
        return [WeatherDataPublic.model_validate(data)] if data else []
    return [
        WeatherDataPublic.model_validate(data)
        for data in crud_weather_data.get_multi(session, skip=skip, limit=limit)
    ]


@router.get("/stocks/cache", response_model=List[StockDataPublic])
def get_stocks_cache(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    symbol: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[StockDataPublic]:
    """Get cached stock data."""
    from app.modules.integrations.crud.integrations_crud import crud_stock_data

    if symbol:
        data = crud_stock_data.get_by_symbol(session, symbol)
        return [StockDataPublic.model_validate(data)] if data else []
    return [
        StockDataPublic.model_validate(data)
        for data in crud_stock_data.get_multi(session, skip=skip, limit=limit)
    ]


@router.get("/sports/cache", response_model=List[SportsDataPublic])
def get_sports_cache(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    sport: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[SportsDataPublic]:
    """Get cached sports data."""
    from app.modules.integrations.crud.integrations_crud import crud_sports_data

    if sport and status:
        if status == "live":
            data = crud_sports_data.get_live_events(session, sport)
        else:
            data = crud_sports_data.get_upcoming_events(session, sport, limit)
        return [SportsDataPublic.model_validate(item) for item in data]
    return [
        SportsDataPublic.model_validate(data)
        for data in crud_sports_data.get_multi(session, skip=skip, limit=limit)
    ]


# Analytics and Statistics Endpoints
@router.get("/stats/integrations", response_model=IntegrationStatsResponse)
def get_integration_stats(
    *, session: SessionDep, current_user: CurrentUser
) -> IntegrationStatsResponse:
    """Get integration statistics."""
    service = IntegrationsService(session)
    return service.get_integration_stats()


@router.get("/stats/webhooks", response_model=WebhookStatsResponse)
def get_webhook_stats(
    *, session: SessionDep, current_user: CurrentUser
) -> WebhookStatsResponse:
    """Get webhook statistics."""
    service = IntegrationsService(session)
    return service.get_webhook_stats()


@router.get("/stats/api-keys", response_model=APIKeyStatsResponse)
def get_api_key_stats(
    *, session: SessionDep, current_user: CurrentUser
) -> APIKeyStatsResponse:
    """Get API key statistics."""
    service = IntegrationsService(session)
    return service.get_api_key_stats()


@router.get("/sync/logs", response_model=List[IntegrationSyncLogPublic])
def get_sync_logs(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    integration_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[IntegrationSyncLogPublic]:
    """Get integration sync logs."""
    from app.modules.integrations.crud.integrations_crud import (
        crud_integration_sync_log,
    )

    if integration_id:
        logs = crud_integration_sync_log.get_by_integration(
            session, integration_id, limit
        )
    else:
        logs = crud_integration_sync_log.get_recent_syncs(session, hours)

    if status:
        logs = [log for log in logs if log.status == status]

    return [
        IntegrationSyncLogPublic.model_validate(log)
        for log in logs[skip : skip + limit]
    ]


# Utility Endpoints
@router.post("/cleanup/weather", response_model=Dict[str, int])
def cleanup_weather_cache(
    *, session: SessionDep, current_user: CurrentUser
) -> Dict[str, int]:
    """Clean up expired weather data."""
    from app.modules.integrations.crud.integrations_crud import crud_weather_data

    removed = crud_weather_data.cleanup_expired(session)
    return {"removed_weather_records": removed}


@router.post("/cleanup/stocks", response_model=Dict[str, int])
def cleanup_stocks_cache(
    *, session: SessionDep, current_user: CurrentUser
) -> Dict[str, int]:
    """Clean up expired stock data."""
    from app.modules.integrations.crud.integrations_crud import crud_stock_data

    removed = crud_stock_data.cleanup_expired(session)
    return {"removed_stock_records": removed}


@router.post("/cleanup/sports", response_model=Dict[str, int])
def cleanup_sports_cache(
    *, session: SessionDep, current_user: CurrentUser
) -> Dict[str, int]:
    """Clean up expired sports data."""
    from app.modules.integrations.crud.integrations_crud import crud_sports_data

    removed = crud_sports_data.cleanup_expired(session)
    return {"removed_sports_records": removed}


@router.post("/cleanup/expired-api-keys", response_model=Dict[str, int])
def cleanup_expired_api_keys(
    *, session: SessionDep, current_user: CurrentUser
) -> Dict[str, int]:
    """Clean up expired API keys."""
    from app.modules.integrations.crud.integrations_crud import crud_api_key

    expired_keys = crud_api_key.get_expired(session)
    for key in expired_keys:
        crud_api_key.update(session, db_obj=key, obj_in={"is_active": False})
    return {"deactivated_expired_keys": len(expired_keys)}
