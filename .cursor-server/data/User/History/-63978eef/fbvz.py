"""Security utilities."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_bcrypt_secret(secret: str) -> str:
    """Ensure a bcrypt secret is within the 72-byte limit.

    Bcrypt only considers the first 72 bytes of the input. Passlib raises
    a ValueError when the input exceeds this limit. We proactively truncate
    to avoid runtime crashes while keeping behaviour consistent with bcrypt's
    native handling.
    """
    secret_bytes = secret.encode("utf-8")
    if len(secret_bytes) > 72:
        secret_bytes = secret_bytes[:72]
    return secret_bytes.decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(_normalize_bcrypt_secret(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(_normalize_bcrypt_secret(password))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        # Log the error for debugging (optional, can be removed in production)
        import logging
        logging.debug(f"Token verification failed: {str(e)}")
        return None

