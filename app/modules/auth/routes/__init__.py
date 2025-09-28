from app.modules.auth.routes.auth import router as auth_router
from app.modules.auth.routes.oauth import router as oauth_router
from app.modules.auth.routes.two_factor import router as two_factor_router

__all__ = ["auth_router", "oauth_router", "two_factor_router"]
