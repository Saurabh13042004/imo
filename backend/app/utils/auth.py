"""Authentication utility functions for password hashing and JWT token management."""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
from passlib.context import CryptContext
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_tokens(user_id: str, email: str, roles: list[str]) -> Tuple[str, str]:
    """Create access and refresh JWT tokens.
    
    Args:
        user_id: User UUID
        email: User email
        roles: List of user roles
        
    Returns:
        Tuple of (access_token, refresh_token)
    """
    # Access token payload
    access_payload = {
        "user_id": str(user_id),
        "email": email,
        "roles": roles,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow(),
    }
    
    # Refresh token payload
    refresh_payload = {
        "user_id": str(user_id),
        "email": email,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
        "iat": datetime.utcnow(),
    }
    
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return access_token, refresh_token


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_expiration_time(token: str) -> Optional[int]:
    """Get the expiration time of a token in seconds.
    
    Args:
        token: JWT token string
        
    Returns:
        Seconds until expiration, or None if token is invalid
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    exp = payload.get("exp")
    if not exp:
        return None
    
    return exp - int(datetime.utcnow().timestamp())
