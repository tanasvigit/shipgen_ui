from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt

from app.core.config import settings


# Use bcrypt directly to avoid passlib compatibility issues
def _hash_password_bcrypt(password: str) -> str:
    """Hash password using bcrypt directly."""
    # Ensure password is bytes
    if isinstance(password, str):
        password = password.encode('utf-8')
    # Truncate to 72 bytes (bcrypt limit)
    if len(password) > 72:
        password = password[:72]
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')


def _verify_password_bcrypt(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt directly."""
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback to direct bcrypt if passlib fails
        return _verify_password_bcrypt(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    # Ensure password is a string
    if isinstance(password, bytes):
        password = password.decode('utf-8')
    
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    # Try passlib first, fallback to direct bcrypt if it fails
    try:
        return pwd_context.hash(password)
    except (ValueError, AttributeError) as e:
        # Fallback to direct bcrypt hashing
        return _hash_password_bcrypt(password)


def create_access_token(subject: str, token_type: Optional[str] = None, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: dict[str, Any] = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    if token_type:
        to_encode["type"] = token_type

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")



