from fastapi import APIRouter

from app.modules.live_streams.routes import (
    badges_router,
    streams_router,
    viewers_router,
)

router = APIRouter()

# Include sub-routers
router.include_router(
    streams_router,
    prefix="/streams",
    tags=["live-streams"],
)

router.include_router(
    viewers_router,
    prefix="/streams",
    tags=["live-stream-viewers"],
)

router.include_router(
    badges_router,
    prefix="/streams",
    tags=["live-stream-badges"],
)

__all__ = ["router"]
