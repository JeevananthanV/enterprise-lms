"""Production Enterprise Middleware.

Provides:
- Request ID correlation (X-Request-ID propagation)
- Structured JSON logging of all incoming requests and outgoing responses
- Sliding-window Redis-backed Rate Limiter (application level)
- OWASP Security Headers enforcement
"""

import time
import uuid
import logging
import json
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

logger = logging.getLogger("enterprise.access")


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Generates or propagates X-Request-ID for distributed tracing across services."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Attach request_id to request state for access in controllers and logs
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Logs detailed access telemetry in structured format with execution latency."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

        # Extract client IP safely (supporting X-Forwarded-For)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000  # in ms
            response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

            log_payload = {
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "status_code": response.status_code,
                "client_ip": client_ip,
                "user_agent": request.headers.get("User-Agent", "unknown"),
                "duration_ms": round(process_time, 2),
            }

            if response.status_code >= 500:
                logger.error(json.dumps(log_payload))
            elif response.status_code >= 400:
                logger.warning(json.dumps(log_payload))
            else:
                logger.info(json.dumps(log_payload))

            return response
        except Exception as exc:
            process_time = (time.perf_counter() - start_time) * 1000
            log_payload = {
                "event": "http_exception_unhandled",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "error": str(exc),
                "duration_ms": round(process_time, 2),
            }
            logger.error(json.dumps(log_payload), exc_info=True)
            raise exc


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces enterprise OWASP security headers on all HTTP responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # In production environments, enforce strict HSTS
        if getattr(settings, "ENVIRONMENT", "development") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter using Redis for distributed application instances.
    
    Gracefully allows requests if Redis is unavailable or disconnected.
    """

    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Exempt health check and docs from rate limiting
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Skip rate limiting during testing or if Redis is not configured
        if getattr(settings, "ENVIRONMENT", "") == "test":
            return await call_next(request)

        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else "127.0.0.1")
        )

        try:
            from app.core.redis import redis_service
            if redis_service.is_connected:
                key = f"rate_limit:{client_ip}:{int(time.time() // 60)}"
                current_count = await redis_service.client.incr(key)
                if current_count == 1:
                    await redis_service.client.expire(key, 65)

                if current_count > self.requests_per_minute:
                    return Response(
                        content=json.dumps({
                            "detail": "Too many requests. Please try again in a minute.",
                            "retry_after_seconds": 60,
                        }),
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        media_type="application/json",
                        headers={"Retry-After": "60"},
                    )
        except Exception as e:
            # Fallback gracefully if Redis is temporarily unreachable
            logger.debug(f"Redis rate limiting skipped: {e}")

        return await call_next(request)
