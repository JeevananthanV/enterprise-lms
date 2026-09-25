from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel, Field


class SubsystemHealth(BaseModel):
    postgresql: str = Field(default="configured")
    mongodb: str = Field(default="configured")
    redis: str = Field(default="configured")


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Overall system health status")
    app_name: str = Field(default="Enterprise LMS")
    environment: str = Field(default="development")
    version: str = Field(default="0.1.0")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    subsystems: Optional[SubsystemHealth] = None
