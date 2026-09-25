# ==============================================================================
# Multi-Stage Production Dockerfile for Enterprise LMS Backend
# ==============================================================================

# Build Stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools and compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies in isolated wheel directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Runtime Stage
FROM python:3.11-slim AS runtime

# Create unprivileged system user & group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Copy application source code
COPY --chown=appuser:appgroup . /app

# Switch to unprivileged user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch production server with Gunicorn process manager and Uvicorn workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*"]
