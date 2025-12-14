"""Security utilities."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
from app.core.config import get_settings

settings = get_settings()


def _normalize_bcrypt_secret(secret: str) -> bytes:
    """Ensure a bcrypt secret is within the 72-byte limit.

    Bcrypt only considers the first 72 bytes of the input. We proactively truncate
    to avoid runtime crashes while keeping behaviour consistent with bcrypt's
    native handling.
    """
    secret_bytes = secret.encode("utf-8")
    if len(secret_bytes) > 72:
        return secret_bytes[:72]
    return secret_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        normalized = _normalize_bcrypt_secret(plain_password)
        return bcrypt.checkpw(normalized, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    normalized = _normalize_bcrypt_secret(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(normalized, salt)
    return hashed.decode('utf-8')


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

