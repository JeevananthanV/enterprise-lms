from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Set, Union
import bcrypt
import jwt
from app.core.config import settings
from app.core.logging import logger
from app.db.redis import get_redis

# In-memory token blocklist fallback if Redis is unavailable
_memory_blocklist: Set[str] = set()


def hash_password(password: str) -> str:
    """Securely hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception as e:
        logger.warning(f"Password verification encountered error: {e}")
        return False


def create_access_token(
    subject: Union[str, int],
    role: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, int],
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT refresh token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token payload."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token signature has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {e}")


async def blocklist_token(token: str, expires_seconds: int = 3600) -> None:
    """Add a revoked token to the blocklist (Redis with in-memory fallback)."""
    redis_client = get_redis()
    if redis_client is not None:
        try:
            await redis_client.setex(f"bl_{token}", expires_seconds, "revoked")
            return
        except Exception as e:
            logger.warning(f"Redis blocklist set failed, falling back to memory: {e}")

    _memory_blocklist.add(token)


async def is_token_blocklisted(token: str) -> bool:
    """Check if a token has been revoked."""
    if token in _memory_blocklist:
        return True

    redis_client = get_redis()
    if redis_client is not None:
        try:
            val = await redis_client.get(f"bl_{token}")
            return val is not None
        except Exception as e:
            logger.warning(f"Redis blocklist check failed: {e}")

    return False
