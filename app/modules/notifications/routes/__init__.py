from fastapi import APIRouter

from app.modules.notifications.routes.devices import router as devices_router
from app.modules.notifications.routes.notifications import (
    router as notifications_router,
)
from app.modules.notifications.routes.preferences import router as preferences_router

router = APIRouter()
router.include_router(
    notifications_router, prefix="/notifications", tags=["notifications"]
)
router.include_router(devices_router, prefix="/devices", tags=["devices"])
router.include_router(preferences_router, prefix="/preferences", tags=["preferences"])
