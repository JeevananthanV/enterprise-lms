from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Core Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Enterprise LMS"
    API_V1_STR: str = "/api/v1"

    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i).strip() for i in v if str(i).strip()]
        return []

    # Relational Database (PostgreSQL / SQLAlchemy Async)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_lms"

    # Document Database (MongoDB - Optional in Local Development)
    MONGODB_ENABLED: bool = False
    MONGODB_URL: str = "mongodb://root:example@localhost:27017"
    MONGODB_DB_NAME: str = "enterprise_lms_content"
    MONGODB_TIMEOUT_MS: int = 1000

    # Ephemeral & Cache Store (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL_SECONDS: int = 300
    CACHE_COURSE_CATALOG_TTL_SECONDS: int = 300
    CACHE_COURSE_DETAILS_TTL_SECONDS: int = 600
    CACHE_ANALYTICS_TTL_SECONDS: int = 120

    # JWT & Security Configuration
    JWT_SECRET: str = "temporary-development-secret-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v.encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET must be at least 32 bytes (256 bits) for secure HS256 encryption.")
        return v

    # Initial Seed Configuration (Local Development Only)
    SEED_DEMO_USERS: bool = True
    SEED_ADMIN_EMAIL: str = "admin@lms.enterprise.local"
    SEED_ADMIN_PASSWORD: Optional[str] = None
    SEED_INSTRUCTOR_EMAIL: str = "instructor@lms.enterprise.local"
    SEED_INSTRUCTOR_PASSWORD: Optional[str] = None
    SEED_STUDENT_EMAIL: str = "student@lms.enterprise.local"
    SEED_STUDENT_PASSWORD: Optional[str] = None


settings = Settings()
