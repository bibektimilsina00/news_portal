from fastapi import APIRouter

from app.modules.ai_features.routes import ai_features_router
from app.modules.analytics.routes import analytics_router
from app.modules.auth.routes import auth_router, oauth_router, two_factor_router
from app.modules.content_moderation.routes import (
    router as get_content_moderation_router,
)
from app.modules.integrations.routes import integrations_router
from app.modules.live_streams.routes.badges import router as live_streams_badges_router
from app.modules.live_streams.routes.main import router as live_streams_router
from app.modules.live_streams.routes.viewers import (
    router as live_streams_viewers_router,
)

# from app.modules.media.routes import router as media_router
# from app.modules.media.routes.images import router as media_images_router
# from app.modules.media.routes.videos import router as media_videos_router
from app.modules.messaging.routes import (
    conversations_router,
    messages_router,
    participants_router,
)
from app.modules.monetization.routes import router as monetization_router
from app.modules.news.routes.news import router as news_router
from app.modules.notifications.routes import router as notifications_router
from app.modules.notifications.routes.devices import (
    router as notifications_devices_router,
)
from app.modules.notifications.routes.preferences import (
    router as notifications_preferences_router,
)
from app.modules.posts.routes.posts import router as posts_router
from app.modules.reels.routes.effects import router as effects_router
from app.modules.reels.routes.music import router as music_router
from app.modules.reels.routes.reels import router as reels_router
from app.modules.search.routes import history_router, search_router, trending_router
from app.modules.stories.routes.highlights import router as highlights_router
from app.modules.stories.routes.interactions import router as interactions_router
from app.modules.stories.routes.stories import router as stories_router
from app.modules.stories.routes.viewers import router as viewers_router
from app.modules.users.routes import profile, users, verification
from app.shared.routes.health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(oauth_router, prefix="/auth", tags=["oauth"])
api_router.include_router(two_factor_router, prefix="/auth", tags=["two-factor"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profile.router, prefix="/users", tags=["profile"])
api_router.include_router(verification.router, prefix="/users", tags=["verification"])
api_router.include_router(posts_router, prefix="/posts", tags=["posts"])
api_router.include_router(news_router, prefix="/news", tags=["news"])
api_router.include_router(stories_router, prefix="/stories", tags=["stories"])
api_router.include_router(
    highlights_router, prefix="/stories", tags=["story-highlights"]
)
api_router.include_router(
    interactions_router, prefix="/stories", tags=["story-interactions"]
)
api_router.include_router(viewers_router, prefix="/stories", tags=["story-viewers"])
api_router.include_router(reels_router, prefix="/reels", tags=["reels"])
api_router.include_router(music_router, prefix="/reels", tags=["reel-music"])
api_router.include_router(effects_router, prefix="/reels", tags=["reel-effects"])
api_router.include_router(
    live_streams_router, prefix="/live-streams", tags=["live-streams"]
)
api_router.include_router(
    live_streams_viewers_router, prefix="/live-streams", tags=["live-stream-viewers"]
)
api_router.include_router(
    live_streams_badges_router, prefix="/live-streams", tags=["live-stream-badges"]
)
api_router.include_router(
    conversations_router,
    prefix="/messaging/conversations",
    tags=["messaging-conversations"],
)
api_router.include_router(
    messages_router, prefix="/messaging/messages", tags=["messaging-messages"]
)
api_router.include_router(
    participants_router,
    prefix="/messaging/participants",
    tags=["messaging-participants"],
)
api_router.include_router(
    notifications_router, prefix="/notifications", tags=["notifications"]
)
api_router.include_router(
    notifications_devices_router,
    prefix="/notifications/devices",
    tags=["notification-devices"],
)
api_router.include_router(
    notifications_preferences_router,
    prefix="/notifications/preferences",
    tags=["notification-preferences"],
)
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(
    history_router, prefix="/search/history", tags=["search-history"]
)
api_router.include_router(
    trending_router, prefix="/search/trending", tags=["search-trending"]
)
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
# api_router.include_router(media_router, prefix="/media", tags=["media"])
# api_router.include_router(
#     media_images_router, prefix="/media/images", tags=["media-images"]
# )
# api_router.include_router(
#     media_videos_router, prefix="/media/videos", tags=["media-videos"]
# )
api_router.include_router(
    monetization_router, prefix="/monetization", tags=["monetization"]
)
api_router.include_router(
    get_content_moderation_router, prefix="/moderation", tags=["content-moderation"]
)
api_router.include_router(
    ai_features_router, prefix="/ai-features", tags=["ai-features"]
)
api_router.include_router(
    integrations_router, prefix="/integrations", tags=["integrations"]
)
