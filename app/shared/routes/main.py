from fastapi import APIRouter

from app.modules.analytics.routes import analytics_router
from app.modules.content_moderation.routes import router as content_moderation_router
from app.modules.live_streams.routes.main import router as live_streams_router
from app.modules.media.routes import router as media_router
from app.modules.messaging.routes import (
    conversations_router,
    messages_router,
    participants_router,
)
from app.modules.monetization.routes import router as monetization_router
from app.modules.news.routes.news import router as news_router
from app.modules.notifications.routes import router as notifications_router
from app.modules.posts.routes.posts import router as posts_router
from app.modules.reels.routes.effects import router as effects_router
from app.modules.reels.routes.music import router as music_router
from app.modules.reels.routes.reels import router as reels_router
from app.modules.search.routes import history_router, search_router, trending_router
from app.modules.stories.routes.highlights import router as highlights_router
from app.modules.stories.routes.interactions import router as interactions_router
from app.modules.stories.routes.stories import router as stories_router
from app.modules.stories.routes.viewers import router as viewers_router
from app.modules.users.crud import login
from app.modules.users.routes import profile, users, verification

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
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
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(
    history_router, prefix="/search/history", tags=["search-history"]
)
api_router.include_router(
    trending_router, prefix="/search/trending", tags=["search-trending"]
)
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(media_router, prefix="/media", tags=["media"])
api_router.include_router(
    monetization_router, prefix="/monetization", tags=["monetization"]
)
api_router.include_router(
    content_moderation_router, prefix="/moderation", tags=["content-moderation"]
)
