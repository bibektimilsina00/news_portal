from fastapi import APIRouter

from app.modules.news.routes import items
from app.modules.users.crud import login
from app.modules.users.routes import users

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
