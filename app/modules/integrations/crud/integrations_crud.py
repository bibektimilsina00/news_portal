from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, func, or_, select
from sqlmodel import Session

from app.modules.integrations.model.integrations import (
    APIKey,
    APIRequestLog,
    ExternalNewsArticle,
    Integration,
    IntegrationNewsSource,
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
    APIKeyUpdate,
    APIRequestLogCreate,
    ExternalNewsArticleCreate,
    ExternalNewsArticleUpdate,
    IntegrationCreate,
    IntegrationSyncLogCreate,
    IntegrationUpdate,
    NewsSourceCreate,
    NewsSourceUpdate,
    SocialMediaPostCreate,
    SocialMediaPostUpdate,
    SportsDataCreate,
    SportsDataUpdate,
    StockDataCreate,
    StockDataUpdate,
    WeatherDataCreate,
    WeatherDataUpdate,
    WebhookCreate,
    WebhookDeliveryCreate,
    WebhookDeliveryUpdate,
    WebhookUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDIntegration(CRUDBase[Integration, IntegrationCreate, IntegrationUpdate]):
    def get_by_provider(self, session: Session, provider: str) -> Optional[Integration]:
        return session.exec(
            select(Integration).where(Integration.provider == provider)
        ).first()

    def get_by_type(self, session: Session, integration_type: str) -> List[Integration]:
        return session.exec(
            select(Integration).where(Integration.integration_type == integration_type)
        ).all()

    def get_active(self, session: Session) -> List[Integration]:
        return session.exec(
            select(Integration).where(Integration.status == "active")
        ).all()

    def update_sync_status(
        self,
        session: Session,
        integration_id: UUID,
        success: bool,
        error_message: Optional[str] = None,
    ) -> Integration:
        integration = self.get(session, id=integration_id)
        if integration:
            integration.last_sync_at = datetime.utcnow()
            if success:
                integration.success_count += 1
            else:
                integration.error_count += 1
                if error_message:
                    integration.metadata = integration.metadata or {}
                    integration.metadata["last_error"] = error_message
            session.commit()
            session.refresh(integration)
        return integration


class CRUDWebhook(CRUDBase[Webhook, WebhookCreate, WebhookUpdate]):
    def get_by_integration(
        self, session: Session, integration_id: UUID
    ) -> List[Webhook]:
        return session.exec(
            select(Webhook).where(Webhook.integration_id == integration_id)
        ).all()

    def get_active_by_event(self, session: Session, event: str) -> List[Webhook]:
        return session.exec(
            select(Webhook).where(
                and_(
                    Webhook.is_active == True,
                    func.json_contains(Webhook.events, f'["{event}"]'),
                )
            )
        ).all()

    def update_trigger_stats(
        self, session: Session, webhook_id: UUID, success: bool
    ) -> Webhook:
        webhook = self.get(session, id=webhook_id)
        if webhook:
            webhook.last_triggered_at = datetime.utcnow()
            if success:
                webhook.success_count += 1
            else:
                webhook.failure_count += 1
            session.commit()
            session.refresh(webhook)
        return webhook


class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, APIKeyUpdate]):
    def get_by_key_hash(self, session: Session, key_hash: str) -> Optional[APIKey]:
        return session.exec(select(APIKey).where(APIKey.key_hash == key_hash)).first()

    def get_active_by_integration(
        self, session: Session, integration_id: UUID
    ) -> List[APIKey]:
        return session.exec(
            select(APIKey).where(
                and_(
                    APIKey.integration_id == integration_id,
                    APIKey.is_active == True,
                    or_(
                        APIKey.expires_at.is_(None),
                        APIKey.expires_at > datetime.utcnow(),
                    ),
                )
            )
        ).all()

    def update_usage(self, session: Session, api_key_id: UUID) -> APIKey:
        api_key = self.get(session, id=api_key_id)
        if api_key:
            api_key.last_used_at = datetime.utcnow()
            api_key.usage_count += 1
            session.commit()
            session.refresh(api_key)
        return api_key

    def get_expired(self, session: Session) -> List[APIKey]:
        return session.exec(
            select(APIKey).where(
                and_(
                    APIKey.expires_at.is_not(None),
                    APIKey.expires_at <= datetime.utcnow(),
                )
            )
        ).all()


class CRUDSocialMediaPost(
    CRUDBase[SocialMediaPost, SocialMediaPostCreate, SocialMediaPostUpdate]
):
    def get_by_content(
        self, session: Session, content_id: UUID, platform: Optional[str] = None
    ) -> List[SocialMediaPost]:
        query = select(SocialMediaPost).where(SocialMediaPost.content_id == content_id)
        if platform:
            query = query.where(SocialMediaPost.platform == platform)
        return session.exec(query).all()

    def get_pending_posts(
        self, session: Session, platform: Optional[str] = None
    ) -> List[SocialMediaPost]:
        query = select(SocialMediaPost).where(SocialMediaPost.status == "pending")
        if platform:
            query = query.where(SocialMediaPost.platform == platform)
        return session.exec(query).all()

    def update_post_status(
        self,
        session: Session,
        post_id: UUID,
        status: str,
        external_id: Optional[str] = None,
        post_url: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> SocialMediaPost:
        post = self.get(session, id=post_id)
        if post:
            post.status = status
            if external_id:
                post.external_id = external_id
            if post_url:
                post.post_url = post_url
            if error_message:
                post.error_message = error_message
            if status == "posted":
                post.posted_at = datetime.utcnow()
            session.commit()
            session.refresh(post)
        return post


class CRUDNewsSource(
    CRUDBase[IntegrationNewsSource, NewsSourceCreate, NewsSourceUpdate]
):
    def get_by_external_id(
        self, session: Session, external_id: str
    ) -> Optional[IntegrationNewsSource]:
        return session.exec(
            select(IntegrationNewsSource).where(
                IntegrationNewsSource.external_id == external_id
            )
        ).first()

    def get_active_by_integration(
        self, session: Session, integration_id: UUID
    ) -> List[IntegrationNewsSource]:
        return session.exec(
            select(IntegrationNewsSource).where(
                and_(
                    IntegrationNewsSource.integration_id == integration_id,
                    IntegrationNewsSource.is_active == True,
                )
            )
        ).all()

    def update_fetch_stats(
        self, session: Session, source_id: UUID, articles_count: int
    ) -> Optional[IntegrationNewsSource]:
        source = self.get(session, id=source_id)
        if source:
            source.last_fetched_at = datetime.utcnow()
            source.article_count += articles_count
            session.commit()
            session.refresh(source)
        return source


class CRUDExternalNewsArticle(
    CRUDBase[ExternalNewsArticle, ExternalNewsArticleCreate, ExternalNewsArticleUpdate]
):
    def get_by_external_id(
        self, session: Session, external_id: str
    ) -> Optional[ExternalNewsArticle]:
        return session.exec(
            select(ExternalNewsArticle).where(
                ExternalNewsArticle.external_id == external_id
            )
        ).first()

    def get_unimported(
        self, session: Session, limit: int = 100
    ) -> List[ExternalNewsArticle]:
        return session.exec(
            select(ExternalNewsArticle)
            .where(ExternalNewsArticle.is_imported == False)
            .limit(limit)
        ).all()

    def get_by_source(
        self, session: Session, source_id: UUID, limit: int = 50
    ) -> List[ExternalNewsArticle]:
        return session.exec(
            select(ExternalNewsArticle)
            .where(ExternalNewsArticle.source_id == source_id)
            .order_by(ExternalNewsArticle.published_at.desc())
            .limit(limit)
        ).all()

    def mark_imported(self, session: Session, article_id: UUID) -> ExternalNewsArticle:
        article = self.get(session, id=article_id)
        if article:
            article.is_imported = True
            article.imported_at = datetime.utcnow()
            session.commit()
            session.refresh(article)
        return article

    def get_recent_by_category(
        self, session: Session, category: str, limit: int = 20
    ) -> List[ExternalNewsArticle]:
        return session.exec(
            select(ExternalNewsArticle)
            .join(NewsSource)
            .where(
                and_(
                    NewsSource.category == category,
                    ExternalNewsArticle.published_at
                    >= datetime.utcnow() - timedelta(days=7),
                )
            )
            .order_by(ExternalNewsArticle.published_at.desc())
            .limit(limit)
        ).all()


class CRUDWebhookDelivery(
    CRUDBase[WebhookDelivery, WebhookDeliveryCreate, WebhookDeliveryUpdate]
):
    def get_by_webhook(
        self, session: Session, webhook_id: UUID, limit: int = 50
    ) -> List[WebhookDelivery]:
        return session.exec(
            select(WebhookDelivery)
            .where(WebhookDelivery.webhook_id == webhook_id)
            .order_by(WebhookDelivery.created_at.desc())
            .limit(limit)
        ).all()

    def get_recent_failures(
        self, session: Session, hours: int = 24
    ) -> List[WebhookDelivery]:
        return session.exec(
            select(WebhookDelivery)
            .where(
                and_(
                    WebhookDelivery.response_status >= 400,
                    WebhookDelivery.created_at
                    >= datetime.utcnow() - timedelta(hours=hours),
                )
            )
            .order_by(WebhookDelivery.created_at.desc())
        ).all()

    def update_delivery_status(
        self,
        session: Session,
        delivery_id: UUID,
        response_status: int,
        response_body: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> WebhookDelivery:
        delivery = self.get(session, id=delivery_id)
        if delivery:
            delivery.response_status = response_status
            delivery.response_body = response_body
            delivery.error_message = error_message
            delivery.delivered_at = datetime.utcnow()
            session.commit()
            session.refresh(delivery)
        return delivery


class CRUDAPIRequestLog(
    CRUDBase[APIRequestLog, APIRequestLogCreate, APIRequestLogCreate]
):
    def get_by_key(
        self, session: Session, api_key_id: UUID, limit: int = 100
    ) -> List[APIRequestLog]:
        return session.exec(
            select(APIRequestLog)
            .where(APIRequestLog.api_key_id == api_key_id)
            .order_by(APIRequestLog.created_at.desc())
            .limit(limit)
        ).all()

    def get_recent_requests(
        self, session: Session, hours: int = 24
    ) -> List[APIRequestLog]:
        return session.exec(
            select(APIRequestLog)
            .where(
                APIRequestLog.created_at >= datetime.utcnow() - timedelta(hours=hours)
            )
            .order_by(APIRequestLog.created_at.desc())
        ).all()

    def get_endpoint_stats(
        self, session: Session, hours: int = 24
    ) -> List[Dict[str, Any]]:
        # Get endpoint usage statistics
        result = session.exec(
            select(
                APIRequestLog.endpoint,
                func.count(APIRequestLog.id).label("count"),
                func.avg(APIRequestLog.response_time_ms).label("avg_response_time"),
            )
            .where(
                APIRequestLog.created_at >= datetime.utcnow() - timedelta(hours=hours)
            )
            .group_by(APIRequestLog.endpoint)
            .order_by(func.count(APIRequestLog.id).desc())
        ).all()

        return [
            {
                "endpoint": row[0],
                "count": row[1],
                "avg_response_time": float(row[2]) if row[2] else 0,
            }
            for row in result
        ]


class CRUDIntegrationSyncLog(
    CRUDBase[IntegrationSyncLog, IntegrationSyncLogCreate, IntegrationSyncLogCreate]
):
    def get_by_integration(
        self, session: Session, integration_id: UUID, limit: int = 50
    ) -> List[IntegrationSyncLog]:
        return session.exec(
            select(IntegrationSyncLog)
            .where(IntegrationSyncLog.integration_id == integration_id)
            .order_by(IntegrationSyncLog.created_at.desc())
            .limit(limit)
        ).all()

    def get_recent_syncs(
        self, session: Session, hours: int = 24
    ) -> List[IntegrationSyncLog]:
        return session.exec(
            select(IntegrationSyncLog)
            .where(
                IntegrationSyncLog.created_at
                >= datetime.utcnow() - timedelta(hours=hours)
            )
            .order_by(IntegrationSyncLog.created_at.desc())
        ).all()

    def update_sync_result(
        self,
        session: Session,
        sync_log_id: UUID,
        status: str,
        records_processed: int,
        records_failed: int,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> IntegrationSyncLog:
        sync_log = self.get(session, id=sync_log_id)
        if sync_log:
            sync_log.status = status
            sync_log.records_processed = records_processed
            sync_log.records_failed = records_failed
            if duration_ms:
                sync_log.duration_ms = duration_ms
            if error_message:
                sync_log.error_message = error_message
            session.commit()
            session.refresh(sync_log)
        return sync_log


class CRUDWeatherData(CRUDBase[WeatherData, WeatherDataCreate, WeatherDataUpdate]):
    def get_current_by_location(
        self, session: Session, location: str
    ) -> Optional[WeatherData]:
        return session.exec(
            select(WeatherData)
            .where(
                and_(
                    WeatherData.location == location,
                    WeatherData.expires_at > datetime.utcnow(),
                )
            )
            .order_by(WeatherData.fetched_at.desc())
        ).first()

    def cleanup_expired(self, session: Session) -> int:
        result = session.exec(
            delete(WeatherData).where(WeatherData.expires_at <= datetime.utcnow())
        )
        session.commit()
        return result.rowcount


class CRUDStockData(CRUDBase[StockData, StockDataCreate, StockDataUpdate]):
    def get_by_symbol(self, session: Session, symbol: str) -> Optional[StockData]:
        return session.exec(
            select(StockData)
            .where(
                and_(
                    StockData.symbol == symbol, StockData.expires_at > datetime.utcnow()
                )
            )
            .order_by(StockData.fetched_at.desc())
        ).first()

    def get_multiple_symbols(
        self, session: Session, symbols: List[str]
    ) -> List[StockData]:
        return session.exec(
            select(StockData).where(
                and_(
                    StockData.symbol.in_(symbols),
                    StockData.expires_at > datetime.utcnow(),
                )
            )
        ).all()

    def cleanup_expired(self, session: Session) -> int:
        result = session.exec(
            delete(StockData).where(StockData.expires_at <= datetime.utcnow())
        )
        session.commit()
        return result.rowcount


class CRUDSportsData(CRUDBase[SportsData, SportsDataCreate, SportsDataUpdate]):
    def get_live_events(
        self, session: Session, sport: Optional[str] = None
    ) -> List[SportsData]:
        query = select(SportsData).where(
            and_(SportsData.status == "live", SportsData.expires_at > datetime.utcnow())
        )
        if sport:
            query = query.where(SportsData.sport == sport)
        return session.exec(query).all()

    def get_upcoming_events(
        self, session: Session, sport: Optional[str] = None, limit: int = 50
    ) -> List[SportsData]:
        query = (
            select(SportsData)
            .where(
                and_(
                    SportsData.start_time > datetime.utcnow(),
                    SportsData.expires_at > datetime.utcnow(),
                )
            )
            .order_by(SportsData.start_time.asc())
        )
        if sport:
            query = query.where(SportsData.sport == sport)
        return session.exec(query.limit(limit)).all()

    def cleanup_expired(self, session: Session) -> int:
        result = session.exec(
            delete(SportsData).where(SportsData.expires_at <= datetime.utcnow())
        )
        session.commit()
        return result.rowcount


# Create CRUD instances
crud_integration = CRUDIntegration(Integration)
crud_webhook = CRUDWebhook(Webhook)
crud_api_key = CRUDAPIKey(APIKey)
crud_social_media_post = CRUDSocialMediaPost(SocialMediaPost)
crud_news_source = CRUDNewsSource(IntegrationNewsSource)
crud_external_news_article = CRUDExternalNewsArticle(ExternalNewsArticle)
crud_webhook_delivery = CRUDWebhookDelivery(WebhookDelivery)
crud_api_request_log = CRUDAPIRequestLog(APIRequestLog)
crud_integration_sync_log = CRUDIntegrationSyncLog(IntegrationSyncLog)
crud_weather_data = CRUDWeatherData(WeatherData)
crud_stock_data = CRUDStockData(StockData)
crud_sports_data = CRUDSportsData(SportsData)
