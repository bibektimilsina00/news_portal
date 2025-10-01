from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.shared.deps.deps import SessionDep

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check(session: SessionDep):
    """
    Health check endpoint that verifies:
    - Application is running
    - Database connection is working
    - Basic system status
    """
    # Test database connection
    try:
        result = session.execute(text("SELECT 1"))
        result.fetchone()
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",  # You might want to read this from a version file
        "environment": settings.ENVIRONMENT,
        "services": {"database": db_status, "application": "healthy"},
    }


@router.get("/health/db", tags=["health"])
def database_health_check(session: SessionDep):
    """
    Detailed database health check
    """
    try:
        # Test basic connectivity
        result = session.execute(text("SELECT version()"))
        version = result.scalar()

        # Test if we can perform a simple query
        session.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database_version": version,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
