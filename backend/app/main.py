from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.v1.router import api_router
from app.db.mongodb import connect_mongodb, close_mongodb
from app.db.redis import connect_redis, close_redis
from app.schemas.health import HealthResponse, SubsystemHealth
from app.db.session import check_db_health
from app.db.mongodb import check_mongodb_health
from app.db.redis import check_redis_health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager for database & cache connections."""
    logger.info("Initializing Enterprise LMS Application Services...")
    # Initialize database tables
    try:
        from app.db.session import async_engine, AsyncSessionLocal
        from app.models.base import Base
        from app.db.seed import seed_all
        import app.models  # Ensure all LMS models are registered
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema synchronized.")
        async with AsyncSessionLocal() as session:
            await seed_all(session)
    except Exception as e:
        logger.warning(f"Database schema initialization deferred: {e}")

    # Initialize connection pools (non-blocking / graceful fallback if offline)
    await connect_mongodb()
    await connect_redis()
    yield
    logger.info("Shutting down Enterprise LMS Application Services...")
    await close_mongodb()
    await close_redis()


def create_application() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-oriented, domain-driven Enterprise Learning Management System API.",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Enterprise Security Headers Middleware
    from app.core.middleware import (
        RequestCorrelationMiddleware,
        StructuredLoggingMiddleware,
        SecurityHeadersMiddleware,
        RateLimitMiddleware,
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
    app.add_middleware(StructuredLoggingMiddleware)
    app.add_middleware(RequestCorrelationMiddleware)

    # Root Direct Health Endpoint (Convenience & Probe Standard)
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def root_health():
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

    # Root Information Endpoint
    @app.get("/", tags=["Root"])
    async def root_info():
        return {
            "app_name": settings.APP_NAME,
            "version": "0.1.0",
            "status": "running",
            "environment": settings.ENVIRONMENT,
            "docs_url": "/docs",
            "api_v1_url": settings.API_V1_STR,
        }

    # Mount Domain Routers under /api/v1
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )
