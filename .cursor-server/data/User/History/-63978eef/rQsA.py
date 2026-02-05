"""Security utilities."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# Password hashing
# Note: We handle truncation manually in get_password_hash and verify_password
# to avoid bcrypt's 72-byte limit. We use bcrypt__ident="2b" to avoid issues
# during passlib initialization with detect_wrap_bug.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b"  # Use bcrypt 2b identifier to avoid wrap bug detection issues
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Bcrypt has a 72-byte limit for passwords. If the password exceeds this,
    it will be truncated to 72 bytes before verification to match the hashing behavior.
    """
    # Truncate password to 72 bytes if it's longer (bcrypt limit)
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password.
    
    Bcrypt has a 72-byte limit for passwords. If the password exceeds this,
    it will be truncated to 72 bytes to avoid errors.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Truncate password to 72 bytes if it's longer (bcrypt limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        # If still fails, log and re-raise with more context
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to hash password (length: {len(password_bytes)} bytes): {e}")
        raise ValueError(f"Password hashing failed: {e}") from e


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

