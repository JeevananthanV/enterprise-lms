from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse, SubsystemHealth
from app.db.session import check_db_health
from app.db.mongodb import check_mongodb_health
from app.db.redis import check_redis_health

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Readiness Probe",
    description="Returns the operating status of the Enterprise LMS API and optional subsystem indicators.",
)
async def get_health():
    """Health check endpoint providing overall status and subsystem readiness."""
    pg_ok = await check_db_health()
    mongo_ok = await check_mongodb_health()
    redis_ok = await check_redis_health()

    if not settings.MONGODB_ENABLED:
        mongo_status = "optional (disabled / pg-fallback active)"
    elif mongo_ok:
        mongo_status = "connected"
    else:
        mongo_status = "configured (offline / pg-fallback active)"

    subsystems = SubsystemHealth(
        postgresql="connected" if pg_ok else "configured (offline/unreachable)",
        mongodb=mongo_status,
        redis="connected" if redis_ok else "configured (offline/unreachable)",
    )

    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        version="0.1.0",
        subsystems=subsystems,
    )
