from app.modules.search.routes.history import router as history_router
from app.modules.search.routes.search import router as search_router
from app.modules.search.routes.trending import router as trending_router

__all__ = ["search_router", "history_router", "trending_router"]
