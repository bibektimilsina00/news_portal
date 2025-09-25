from fastapi import APIRouter

from app.modules.monetization.routes.monetization import router as monetization_router

router = APIRouter()

# Include sub-routers
router.include_router(monetization_router, prefix="", tags=["monetization"])
