from app.modules.live_streams.routes.badges import router as badges_router
from app.modules.live_streams.routes.streams import router as streams_router
from app.modules.live_streams.routes.viewers import router as viewers_router

__all__ = ["streams_router", "viewers_router", "badges_router"]
