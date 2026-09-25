from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.certificate import Certificate
from app.core.dependencies import require_role
from app.services.cache_service import cache_service
from app.core.config import settings

router = APIRouter()


@router.get("/status")
async def analytics_domain_status():
    return {"domain": "analytics", "status": "registered", "phase": "Phase 8 Caching Enabled"}


@router.get("/summary")
async def get_platform_analytics_summary(
    current_user: User = Depends(require_role(UserRole.PLATFORM_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get high-level platform metrics.
    Cached in Redis with short TTL (CACHE_ANALYTICS_TTL_SECONDS) to balance freshness and performance.
    """
    cache_key = cache_service.generate_analytics_key("platform")
    cached_metrics = await cache_service.get_cached(cache_key)
    if cached_metrics is not None:
        return {**cached_metrics, "from_cache": True}

    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_courses = (await db.execute(select(func.count(Course.id)))).scalar() or 0
    published_courses = (
        await db.execute(
            select(func.count(Course.id)).where(Course.status == CourseStatus.PUBLISHED)
        )
    ).scalar() or 0
    total_students = (
        await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.STUDENT)
        )
    ).scalar() or 0
    total_instructors = (
        await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.INSTRUCTOR)
        )
    ).scalar() or 0
    total_enrollments = (
        await db.execute(select(func.count(Enrollment.id)))
    ).scalar() or 0
    completed_enrollments = (
        await db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.status == EnrollmentStatus.COMPLETED
            )
        )
    ).scalar() or 0
    total_certificates = (
        await db.execute(select(func.count(Certificate.id)))
    ).scalar() or 0

    metrics: Dict[str, Any] = {
        "total_users": total_users,
        "total_courses": total_courses,
        "published_courses": published_courses,
        "total_students": total_students,
        "total_instructors": total_instructors,
        "total_enrollments": total_enrollments,
        "completed_enrollments": completed_enrollments,
        "total_certificates": total_certificates,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    await cache_service.set_cached(
        cache_key,
        metrics,
        ttl_seconds=settings.CACHE_ANALYTICS_TTL_SECONDS,
    )
    return {**metrics, "from_cache": False}
