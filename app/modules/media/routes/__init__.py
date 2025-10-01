from fastapi import APIRouter

from app.modules.media.routes.images import router as images_router
from app.modules.media.routes.media import router as media_router
from app.modules.media.routes.videos import router as videos_router

router = APIRouter()

# Include sub-routers
router.include_router(media_router, prefix="", tags=["media"])
router.include_router(images_router, prefix="/images", tags=["images"])
router.include_router(videos_router, prefix="/videos", tags=["videos"])
