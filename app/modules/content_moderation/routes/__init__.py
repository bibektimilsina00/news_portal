# Lazy import to avoid circular dependencies during model registration
def get_router():
    from app.modules.content_moderation.routes.moderation import router

    return router


__all__ = ["get_router"]
