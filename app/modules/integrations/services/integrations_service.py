import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

import aiohttp
from sqlmodel import Session

from app.modules.integrations.crud.integrations_crud import (
    crud_api_key,
    crud_api_request_log,
    crud_external_news_article,
    crud_integration,
    crud_integration_sync_log,
    crud_news_source,
    crud_social_media_post,
    crud_sports_data,
    crud_stock_data,
    crud_weather_data,
    crud_webhook,
    crud_webhook_delivery,
)
from app.modules.integrations.model.integrations import (
    APIKey,
    Integration,
    IntegrationSyncLog,
    SocialMediaPost,
    SportsData,
    StockData,
    WeatherData,
    Webhook,
    WebhookDelivery,
)
from app.modules.integrations.schema.integrations import (
    APIKeyCreate,
    APIKeyGenerateRequest,
    APIKeyGenerateResponse,
    APIKeyStatsResponse,
    APIRequestLogCreate,
    ExternalNewsArticleCreate,
    IntegrationCreate,
    IntegrationStatsResponse,
    IntegrationSyncLogCreate,
    IntegrationSyncRequest,
    IntegrationSyncResponse,
    IntegrationTestRequest,
    IntegrationTestResponse,
    IntegrationUpdate,
    NewsFetchRequest,
    NewsFetchResponse,
    SocialMediaPostCreate,
    SocialMediaPostRequest,
    SocialMediaPostResponse,
    SportsDataCreate,
    SportsRequest,
    SportsResponse,
    StockDataCreate,
    StockRequest,
    StockResponse,
    WeatherDataCreate,
    WeatherRequest,
    WeatherResponse,
    WebhookCreate,
    WebhookStatsResponse,
    WebhookTriggerRequest,
    WebhookTriggerResponse,
    WebhookUpdate,
)
from app.shared.schema.message import Message


class IntegrationsService:
    def __init__(self, session: Session):
        self.session = session

    # Integration Management
    def create_integration(self, integration_data: IntegrationCreate) -> Integration:
        integration = Integration.model_validate(integration_data)
        return crud_integration.create(self.session, obj_in=integration)

    def update_integration(
        self, integration_id: UUID, integration_data: IntegrationUpdate
    ) -> Integration:
        return crud_integration.update(
            self.session,
            db_obj=crud_integration.get(self.session, id=integration_id),
            obj_in=integration_data,
        )

    def delete_integration(self, integration_id: UUID) -> Message:
        crud_integration.remove(self.session, id=integration_id)
        return Message(message="Integration deleted successfully")

    def get_integration(self, integration_id: UUID) -> Optional[Integration]:
        return crud_integration.get(self.session, id=integration_id)

    def get_integrations(self, skip: int = 0, limit: int = 100) -> List[Integration]:
        return crud_integration.get_multi(self.session, skip=skip, limit=limit)

    async def test_integration(
        self, integration_id: UUID, test_request: IntegrationTestRequest
    ) -> IntegrationTestResponse:
        integration = crud_integration.get(self.session, id=integration_id)
        if not integration:
            return IntegrationTestResponse(
                success=False, message="Integration not found"
            )

        try:
            # Mock integration test - in real implementation, this would call the actual service
            success = True
            message = f"Integration {integration.name} tested successfully"
            response_data = {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

            crud_integration.update_sync_status(
                self.session, integration_id, success=True
            )
            return IntegrationTestResponse(
                success=success, message=message, response_data=response_data
            )

        except Exception as e:
            crud_integration.update_sync_status(
                self.session, integration_id, success=False, error_message=str(e)
            )
            return IntegrationTestResponse(
                success=False,
                message=f"Integration test failed: {str(e)}",
                error_details={"error": str(e)},
            )

    # Webhook Management
    def create_webhook(self, webhook_data: WebhookCreate) -> Webhook:
        webhook = Webhook.model_validate(webhook_data)
        return crud_webhook.create(self.session, obj_in=webhook)

    def update_webhook(self, webhook_id: UUID, webhook_data: WebhookUpdate) -> Webhook:
        return crud_webhook.update(
            self.session,
            db_obj=crud_webhook.get(self.session, id=webhook_id),
            obj_in=webhook_data,
        )

    def delete_webhook(self, webhook_id: UUID) -> Message:
        crud_webhook.remove(self.session, id=webhook_id)
        return Message(message="Webhook deleted successfully")

    def get_webhook(self, webhook_id: UUID) -> Optional[Webhook]:
        return crud_webhook.get(self.session, id=webhook_id)

    def get_webhooks_by_integration(self, integration_id: UUID) -> List[Webhook]:
        return crud_webhook.get_by_integration(self.session, integration_id)

    async def trigger_webhook(
        self, webhook_id: UUID, trigger_request: WebhookTriggerRequest
    ) -> WebhookTriggerResponse:
        webhook = crud_webhook.get(self.session, id=webhook_id)
        if not webhook or not webhook.is_active:
            return WebhookTriggerResponse(
                success=False,
                webhook_id=webhook_id,
                message="Webhook not found or inactive",
            )

        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event=trigger_request.event,
            payload=trigger_request.payload,
        )
        delivery = crud_webhook_delivery.create(self.session, obj_in=delivery)

        try:
            async with aiohttp.ClientSession() as session:
                headers = webhook.headers or {}
                headers["Content-Type"] = "application/json"
                headers["X-Webhook-Signature"] = self._generate_webhook_signature(
                    trigger_request.payload, webhook.secret
                )

                for attempt in range(webhook.retry_count + 1):
                    try:
                        async with session.post(
                            webhook.url,
                            json=trigger_request.payload,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(
                                total=webhook.timeout_seconds
                            ),
                        ) as response:
                            response_body = await response.text()
                            crud_webhook_delivery.update_delivery_status(
                                self.session,
                                delivery.id,
                                response.status,
                                response_body,
                            )

                            if response.status < 400:
                                crud_webhook.update_trigger_stats(
                                    self.session, webhook_id, success=True
                                )
                                return WebhookTriggerResponse(
                                    success=True,
                                    webhook_id=webhook_id,
                                    delivery_id=delivery.id,
                                    message="Webhook triggered successfully",
                                )
                            else:
                                error_msg = f"HTTP {response.status}: {response_body}"
                                break

                    except asyncio.TimeoutError:
                        error_msg = "Request timeout"
                        continue
                    except Exception as e:
                        error_msg = str(e)
                        continue

                # All attempts failed
                crud_webhook_delivery.update_delivery_status(
                    self.session, delivery.id, 500, None, error_msg
                )
                crud_webhook.update_trigger_stats(
                    self.session, webhook_id, success=False
                )
                return WebhookTriggerResponse(
                    success=False,
                    webhook_id=webhook_id,
                    delivery_id=delivery.id,
                    message=f"Webhook delivery failed after {webhook.retry_count + 1} attempts: {error_msg}",
                )

        except Exception as e:
            crud_webhook_delivery.update_delivery_status(
                self.session, delivery.id, 500, None, str(e)
            )
            crud_webhook.update_trigger_stats(self.session, webhook_id, success=False)
            return WebhookTriggerResponse(
                success=False,
                webhook_id=webhook_id,
                delivery_id=delivery.id,
                message=f"Webhook delivery failed: {str(e)}",
            )

    def _generate_webhook_signature(self, payload: Dict[str, Any], secret: str) -> str:
        import hmac
        import json

        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(), payload_str.encode(), hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    # API Key Management
    def generate_api_key(
        self, key_request: APIKeyGenerateRequest
    ) -> APIKeyGenerateResponse:
        # Generate a secure random key
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        api_key_data = APIKeyCreate(
            name=key_request.name,
            description=key_request.description,
            key_hash=key_hash,
            permissions=key_request.permissions,
            rate_limit=key_request.rate_limit,
            expires_at=key_request.expires_at,
        )

        api_key = APIKey.model_validate(api_key_data)
        api_key = crud_api_key.create(self.session, obj_in=api_key)

        return APIKeyGenerateResponse(
            success=True,
            api_key=api_key,
            raw_key=raw_key,
            message="API key generated successfully",
        )

    def revoke_api_key(self, api_key_id: UUID) -> Message:
        api_key = crud_api_key.get(self.session, id=api_key_id)
        if api_key:
            crud_api_key.update(
                self.session, db_obj=api_key, obj_in={"is_active": False}
            )
            return Message(message="API key revoked successfully")
        return Message(message="API key not found")

    def get_api_keys_by_integration(self, integration_id: UUID) -> List[APIKey]:
        return crud_api_key.get_active_by_integration(self.session, integration_id)

    def validate_api_key(self, raw_key: str) -> Optional[APIKey]:
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = crud_api_key.get_by_key_hash(self.session, key_hash)

        if api_key and api_key.is_active:
            # Check expiration
            if api_key.expires_at and api_key.expires_at <= datetime.utcnow():
                return None
            # Update usage
            crud_api_key.update_usage(self.session, api_key.id)
            return api_key
        return None

    def log_api_request(
        self,
        api_key_id: UUID,
        method: str,
        endpoint: str,
        response_status: int,
        response_time_ms: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        log_data = APIRequestLogCreate(
            api_key_id=api_key_id,
            method=method,
            endpoint=endpoint,
            ip_address=ip_address,
            user_agent=user_agent,
            response_status=response_status,
            response_time_ms=response_time_ms,
        )
        crud_api_request_log.create(self.session, obj_in=log_data)

    # Social Media Integration
    async def post_to_social_media(
        self, integration_id: UUID, post_request: SocialMediaPostRequest
    ) -> SocialMediaPostResponse:
        integration = crud_integration.get(self.session, id=integration_id)
        if not integration or integration.status != "active":
            return SocialMediaPostResponse(
                success=False, message="Integration not found or inactive"
            )

        # Create social media post record
        post_data = SocialMediaPostCreate(
            platform=post_request.platform,
            external_id="",  # Will be filled when posted
            content_type=post_request.content_type,
            content_id=post_request.content_id,
            integration_id=integration_id,
        )
        post = SocialMediaPost.model_validate(post_data)
        post = crud_social_media_post.create(self.session, obj_in=post)

        try:
            # Mock social media posting - in real implementation, this would call actual APIs
            external_id = f"mock_{post.id}"
            post_url = f"https://{post_request.platform}.com/post/{external_id}"

            crud_social_media_post.update_post_status(
                self.session, post.id, "posted", external_id, post_url
            )

            crud_integration.update_sync_status(
                self.session, integration_id, success=True
            )
            return SocialMediaPostResponse(
                success=True,
                post_id=external_id,
                post_url=post_url,
                message=f"Posted to {post_request.platform} successfully",
            )

        except Exception as e:
            crud_social_media_post.update_post_status(
                self.session, post.id, "failed", error_message=str(e)
            )
            crud_integration.update_sync_status(
                self.session, integration_id, success=False, error_message=str(e)
            )
            return SocialMediaPostResponse(
                success=False, message=f"Failed to post: {str(e)}"
            )

    # News API Integration
    async def fetch_news(
        self, integration_id: UUID, fetch_request: NewsFetchRequest
    ) -> NewsFetchResponse:
        integration = crud_integration.get(self.session, id=integration_id)
        if not integration or integration.status != "active":
            return NewsFetchResponse(
                success=False, message="Integration not found or inactive"
            )

        try:
            # Mock news fetching - in real implementation, this would call news APIs
            articles_fetched = 0
            sources_updated = 0

            # Get active sources
            sources = crud_news_source.get_active_by_integration(
                self.session, integration_id
            )

            for source in sources:
                if (
                    fetch_request.source_ids
                    and source.id not in fetch_request.source_ids
                ):
                    continue
                if (
                    fetch_request.categories
                    and source.category not in fetch_request.categories
                ):
                    continue

                # Mock article creation
                for i in range(min(fetch_request.limit // len(sources), 5)):
                    article_data = ExternalNewsArticleCreate(
                        title=f"Mock Article {i+1} from {source.name}",
                        description=f"Description for article {i+1}",
                        content=f"Full content for article {i+1} from {source.name}",
                        url=f"https://news.example.com/article-{source.id}-{i+1}",
                        external_id=f"ext_{source.id}_{i+1}",
                        published_at=datetime.utcnow() - timedelta(hours=i),
                        author=f"Author {i+1}",
                        tags=["mock", "news", source.category or "general"],
                        source_id=source.id,
                        integration_id=integration_id,
                    )
                    crud_external_news_article.create(self.session, obj_in=article_data)
                    articles_fetched += 1

                crud_news_source.update_fetch_stats(
                    self.session, source.id, articles_fetched
                )
                sources_updated += 1

            crud_integration.update_sync_status(
                self.session, integration_id, success=True
            )
            return NewsFetchResponse(
                success=True,
                articles_fetched=articles_fetched,
                sources_updated=sources_updated,
                message="News fetched successfully",
            )

        except Exception as e:
            crud_integration.update_sync_status(
                self.session, integration_id, success=False, error_message=str(e)
            )
            return NewsFetchResponse(
                success=False, message=f"Failed to fetch news: {str(e)}"
            )

    # Third-party Service Integrations
    async def get_weather(
        self, integration_id: UUID, weather_request: WeatherRequest
    ) -> WeatherResponse:
        integration = crud_integration.get(self.session, id=integration_id)
        if not integration or integration.status != "active":
            return WeatherResponse(
                success=False, message="Integration not found or inactive"
            )

        # Check cache first
        cached_data = crud_weather_data.get_current_by_location(
            self.session, weather_request.location
        )
        if cached_data:
            return WeatherResponse(
                success=True,
                data=cached_data,
                message="Weather data retrieved from cache",
            )

        try:
            # Mock weather API call - in real implementation, this would call weather APIs
            weather_data = WeatherDataCreate(
                location=weather_request.location,
                temperature_celsius=25.5,
                temperature_fahrenheit=77.9,
                humidity_percent=65,
                wind_speed_kmh=15.2,
                wind_speed_mph=9.4,
                condition="Partly cloudy",
                icon_url="https://weather.example.com/icon/partly-cloudy.png",
                forecast_data=(
                    {"hourly": [], "daily": []}
                    if weather_request.include_forecast
                    else {}
                ),
                integration_id=integration_id,
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )

            weather_record = WeatherData.model_validate(weather_data)
            weather_record = crud_weather_data.create(
                self.session, obj_in=weather_record
            )

            crud_integration.update_sync_status(
                self.session, integration_id, success=True
            )
            return WeatherResponse(
                success=True,
                data=weather_record,
                message="Weather data retrieved successfully",
            )

        except Exception as e:
            crud_integration.update_sync_status(
                self.session, integration_id, success=False, error_message=str(e)
            )
            return WeatherResponse(
                success=False, message=f"Failed to get weather: {str(e)}"
            )

    async def get_stock_data(
        self, integration_id: UUID, stock_request: StockRequest
    ) -> StockResponse:
        integration = crud_integration.get(self.session, id=integration_id)
        if not integration or integration.status != "active":
            return StockResponse(
                success=False, message="Integration not found or inactive"
            )

        try:
            stock_data_list = []

            for symbol in stock_request.symbols:
                # Check cache first
                cached_data = crud_stock_data.get_by_symbol(self.session, symbol)
                if cached_data:
                    stock_data_list.append(cached_data)
                    continue

                # Mock stock API call
                stock_data = StockDataCreate(
                    symbol=symbol,
                    company_name=f"Company {symbol}",
                    current_price=150.25,
                    change_amount=2.50,
                    change_percent=1.69,
                    volume=1000000,
                    market_cap=50000000000,
                    pe_ratio=25.5,
                    historical_data=(
                        {"daily": []} if stock_request.include_history else {}
                    ),
                    integration_id=integration_id,
                    expires_at=datetime.utcnow() + timedelta(minutes=15),
                )

                stock_record = StockData.model_validate(stock_data)
                stock_record = crud_stock_data.create(self.session, obj_in=stock_record)
                stock_data_list.append(stock_record)

            crud_integration.update_sync_status(
                self.session, integration_id, success=True
            )
            return StockResponse(
                success=True,
                data=stock_data_list,
                message="Stock data retrieved successfully",
            )

        except Exception as e:
            crud_integration.update_sync_status(
                self.session, integration_id, success=False, error_message=str(e)
            )
            return StockResponse(
                success=False, message=f"Failed to get stock data: {str(e)}"
            )

    async def get_sports_data(
        self, integration_id: UUID, sports_request: SportsRequest
    ) -> SportsResponse:
        integration = crud_integration.get(self.session, id=integration_id)
        if not integration or integration.status != "active":
            return SportsResponse(
                success=False, message="Integration not found or inactive"
            )

        try:
            # Mock sports API call
            sports_data_list = []

            for i in range(min(sports_request.limit, 10)):
                sports_data = SportsDataCreate(
                    league=sports_request.league or "Premier League",
                    sport=sports_request.sport or "football",
                    event_type="match",
                    event_name=f"Match {i+1}",
                    external_id=f"match_{i+1}",
                    start_time=datetime.utcnow() + timedelta(hours=i * 2),
                    status=sports_request.status or "scheduled",
                    venue=f"Stadium {i+1}",
                    participants=[
                        {"name": f"Team A {i+1}", "score": 0 if i % 2 == 0 else 2},
                        {"name": f"Team B {i+1}", "score": 2 if i % 2 == 0 else 0},
                    ],
                    scores={
                        "home": 0 if i % 2 == 0 else 2,
                        "away": 2 if i % 2 == 0 else 0,
                    },
                    live_stats=(
                        {"possession": {"home": 55, "away": 45}}
                        if sports_request.status == "live"
                        else {}
                    ),
                    integration_id=integration_id,
                    expires_at=datetime.utcnow() + timedelta(hours=2),
                )

                sports_record = SportsData.model_validate(sports_data)
                sports_record = crud_sports_data.create(
                    self.session, obj_in=sports_record
                )
                sports_data_list.append(sports_record)

            crud_integration.update_sync_status(
                self.session, integration_id, success=True
            )
            return SportsResponse(
                success=True,
                data=sports_data_list,
                message="Sports data retrieved successfully",
            )

        except Exception as e:
            crud_integration.update_sync_status(
                self.session, integration_id, success=False, error_message=str(e)
            )
            return SportsResponse(
                success=False, message=f"Failed to get sports data: {str(e)}"
            )

    # Sync Operations
    async def sync_integration(
        self, sync_request: IntegrationSyncRequest
    ) -> IntegrationSyncResponse:
        # Create sync log
        sync_log_data = IntegrationSyncLogCreate(
            integration_id=sync_request.integration_id,
            operation=sync_request.operation,
            status="running",
        )
        sync_log = IntegrationSyncLog.model_validate(sync_log_data)
        sync_log = crud_integration_sync_log.create(self.session, obj_in=sync_log)

        start_time = datetime.utcnow()

        try:
            # Mock sync operation - in real implementation, this would perform actual sync
            records_processed = 42
            records_failed = 2

            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            crud_integration_sync_log.update_sync_result(
                self.session,
                sync_log.id,
                "success",
                records_processed,
                records_failed,
                duration_ms,
            )

            crud_integration.update_sync_status(
                self.session, sync_request.integration_id, success=True
            )
            return IntegrationSyncResponse(
                success=True,
                sync_log_id=sync_log.id,
                records_processed=records_processed,
                records_failed=records_failed,
                message="Integration sync completed successfully",
            )

        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            crud_integration_sync_log.update_sync_result(
                self.session, sync_log.id, "error", 0, 0, duration_ms, str(e)
            )
            crud_integration.update_sync_status(
                self.session,
                sync_request.integration_id,
                success=False,
                error_message=str(e),
            )
            return IntegrationSyncResponse(
                success=False, sync_log_id=sync_log.id, message=f"Sync failed: {str(e)}"
            )

    # Analytics and Statistics
    def get_integration_stats(self) -> IntegrationStatsResponse:
        total_integrations = len(crud_integration.get_multi(self.session))
        active_integrations = len(crud_integration.get_active(self.session))

        # Count by type and status
        all_integrations = crud_integration.get_multi(self.session)
        integrations_by_type = {}
        integrations_by_status = {}

        for integration in all_integrations:
            integrations_by_type[integration.integration_type] = (
                integrations_by_type.get(integration.integration_type, 0) + 1
            )
            integrations_by_status[integration.status] = (
                integrations_by_status.get(integration.status, 0) + 1
            )

        # Recent syncs
        recent_syncs = crud_integration_sync_log.get_recent_syncs(
            self.session, hours=24
        )

        # Today's webhook deliveries and API requests
        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        webhook_deliveries_today = len(
            crud_webhook_delivery.get_recent_failures(self.session, hours=24)
        )  # Approximation
        api_requests_today = len(
            crud_api_request_log.get_recent_requests(self.session, hours=24)
        )

        return IntegrationStatsResponse(
            total_integrations=total_integrations,
            active_integrations=active_integrations,
            integrations_by_type=integrations_by_type,
            integrations_by_status=integrations_by_status,
            recent_syncs=recent_syncs,
            webhook_deliveries_today=webhook_deliveries_today,
            api_requests_today=api_requests_today,
        )

    def get_webhook_stats(self) -> WebhookStatsResponse:
        total_webhooks = len(crud_webhook.get_multi(self.session))
        active_webhooks = len(
            crud_webhook.get_multi(self.session)
        )  # Would need to filter by is_active

        # Recent deliveries
        recent_deliveries = crud_webhook_delivery.get_recent_failures(
            self.session, hours=24
        )

        # Calculate success rate (simplified)
        total_deliveries = len(recent_deliveries)
        success_count = sum(
            1
            for d in recent_deliveries
            if d.response_status and d.response_status < 400
        )
        success_rate = (
            (success_count / total_deliveries) if total_deliveries > 0 else 1.0
        )

        return WebhookStatsResponse(
            total_webhooks=total_webhooks,
            active_webhooks=active_webhooks,
            total_deliveries=total_deliveries,
            success_rate=success_rate,
            recent_deliveries=recent_deliveries,
        )

    def get_api_key_stats(self) -> APIKeyStatsResponse:
        total_keys = len(crud_api_key.get_multi(self.session))
        active_keys = len(
            crud_api_key.get_multi(self.session)
        )  # Would need to filter by is_active

        # Recent requests
        recent_requests = crud_api_request_log.get_recent_requests(
            self.session, hours=24
        )

        # Calculate average response time
        total_requests = len(recent_requests)
        avg_response_time = (
            sum(r.response_time_ms for r in recent_requests) / total_requests
            if total_requests > 0
            else 0
        )

        # Top endpoints
        endpoint_stats = crud_api_request_log.get_endpoint_stats(self.session, hours=24)

        return APIKeyStatsResponse(
            total_keys=total_keys,
            active_keys=active_keys,
            total_requests=total_requests,
            average_response_time=avg_response_time,
            top_endpoints=endpoint_stats,
            recent_requests=recent_requests,
        )
