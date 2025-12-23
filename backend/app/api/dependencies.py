"""API dependencies."""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import Profile
from app.utils.auth import decode_token

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_token_from_request(request: Request) -> Optional[str]:
    """Extract token from Authorization header (optional)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> Profile:
    """Get current authenticated user from JWT token.
    
    Args:
        token: JWT bearer token from Authorization header
        session: Database session
        
    Returns:
        Current user profile
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Decode token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    stmt = select(Profile).where(Profile.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def get_optional_user(
    request: Request,
    session: AsyncSession = Depends(get_db)
) -> Optional[Profile]:
    """Get current user if authenticated, otherwise None.
    
    Args:
        request: HTTP request
        session: Database session
        
    Returns:
        Current user profile or None
    """
    token = get_token_from_request(request)
    
    if not token:
        return None
    
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    stmt = select(Profile).where(Profile.id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


def require_role(*allowed_roles: str):
    """Dependency to require specific roles.
    
    Args:
        allowed_roles: List of allowed role names
        
    Returns:
        Dependency function
    """
    async def check_role(current_user: Profile = Depends(get_current_user)) -> Profile:
        user_roles = []
        # In real implementation, fetch roles from database
        # For now, assume roles are in token
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return check_role
