"""Authentication service for handling user registration, login, and token management."""
import uuid
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import Profile, UserRole
from app.schemas.auth import SignUpRequest, SignInRequest, UserResponse
from app.utils.auth import hash_password, verify_password, create_tokens, decode_token
from app.config import settings


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    async def sign_up(
        session: AsyncSession,
        email: str,
        password: str,
        full_name: str
    ) -> Tuple[Profile, str, str]:
        """Register a new user with email and password.
        
        Args:
            session: Database session
            email: User email
            password: User password (plain text)
            full_name: User full name
            
        Returns:
            Tuple of (user_profile, access_token, refresh_token)
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        stmt = select(Profile).where(Profile.email == email.lower())
        existing_user = await session.execute(stmt)
        if existing_user.scalars().first():
            raise ValueError("Email already registered")
        
        # Create new user profile
        user_id = uuid.uuid4()
        hashed_password = hash_password(password)
        
        profile = Profile(
            id=user_id,
            email=email.lower(),
            full_name=full_name,
            subscription_tier="free",
            access_level="basic",
            password_hash=hashed_password
        )
        
        session.add(profile)
        
        # Assign 'user' role by default
        user_role = UserRole(
            id=uuid.uuid4(),
            user_id=user_id,
            role="user"
        )
        session.add(user_role)
        
        await session.flush()
        await session.commit()
        
        # Create tokens
        access_token, refresh_token = create_tokens(
            user_id=str(user_id),
            email=email.lower(),
            roles=["user"]
        )
        
        return profile, access_token, refresh_token

    @staticmethod
    async def sign_in(
        session: AsyncSession,
        email: str,
        password: str
    ) -> Tuple[Profile, str, str]:
        """Authenticate user with email and password.
        
        Args:
            session: Database session
            email: User email
            password: User password (plain text)
            
        Returns:
            Tuple of (user_profile, access_token, refresh_token)
            
        Raises:
            ValueError: If email not found or password incorrect
        """
        # Find user by email
        stmt = select(Profile).where(Profile.email == email.lower())
        result = await session.execute(stmt)
        profile = result.scalars().first()
        
        if not profile:
            raise ValueError("Email not found")
        
        # Verify password
        if not hasattr(profile, 'password_hash') or not profile.password_hash:
            raise ValueError("Invalid credentials")
        
        if not verify_password(password, profile.password_hash):
            raise ValueError("Incorrect password")
        
        # Get user roles
        roles_stmt = select(UserRole).where(UserRole.user_id == profile.id)
        roles_result = await session.execute(roles_stmt)
        user_roles = roles_result.scalars().all()
        roles = [role.role for role in user_roles]
        
        # Create tokens
        access_token, refresh_token = create_tokens(
            user_id=str(profile.id),
            email=profile.email,
            roles=roles
        )
        
        return profile, access_token, refresh_token

    @staticmethod
    async def refresh_access_token(
        session: AsyncSession,
        refresh_token: str
    ) -> Optional[Tuple[str, str]]:
        """Generate new access token from refresh token.
        
        Args:
            session: Database session
            refresh_token: Refresh token from user
            
        Returns:
            Tuple of (new_access_token, new_refresh_token) or None if invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        # Get user and roles
        stmt = select(Profile).where(Profile.id == user_id)
        result = await session.execute(stmt)
        profile = result.scalars().first()
        
        if not profile:
            return None
        
        # Get user roles
        roles_stmt = select(UserRole).where(UserRole.user_id == profile.id)
        roles_result = await session.execute(roles_stmt)
        user_roles = roles_result.scalars().all()
        roles = [role.role for role in user_roles]
        
        # Create new tokens
        access_token, new_refresh_token = create_tokens(
            user_id=user_id,
            email=email,
            roles=roles
        )
        
        return access_token, new_refresh_token

    @staticmethod
    async def get_user_by_id(
        session: AsyncSession,
        user_id: str
    ) -> Optional[Profile]:
        """Get user profile by ID.
        
        Args:
            session: Database session
            user_id: User UUID
            
        Returns:
            User profile or None
        """
        stmt = select(Profile).where(Profile.id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def change_password(
        session: AsyncSession,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password.
        
        Args:
            session: Database session
            user_id: User UUID
            current_password: Current password (plain text)
            new_password: New password (plain text)
            
        Returns:
            True if successful, False otherwise
        """
        # Get user
        stmt = select(Profile).where(Profile.id == user_id)
        result = await session.execute(stmt)
        profile = result.scalars().first()
        
        if not profile or not hasattr(profile, 'password_hash'):
            return False
        
        # Verify current password
        if not verify_password(current_password, profile.password_hash):
            return False
        
        # Update password
        profile.password_hash = hash_password(new_password)
        session.add(profile)
        await session.commit()
        
        return True

    @staticmethod
    async def get_user_roles(
        session: AsyncSession,
        user_id: str
    ) -> list[str]:
        """Get all roles for a user.
        
        Args:
            session: Database session
            user_id: User UUID
            
        Returns:
            List of role names
        """
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        result = await session.execute(stmt)
        user_roles = result.scalars().all()
        return [role.role for role in user_roles]

    @staticmethod
    async def get_or_create_oauth_user(
        session: AsyncSession,
        email: str,
        full_name: str,
        provider: str,
        provider_id: str,
        avatar_url: Optional[str] = None
    ) -> Tuple[Profile, str, str]:
        """Get existing OAuth user or create new one.
        
        Args:
            session: Database session
            email: User email
            full_name: User full name
            provider: OAuth provider (e.g., 'google')
            provider_id: Provider's user ID
            avatar_url: User's avatar URL
            
        Returns:
            Tuple of (user_profile, access_token, refresh_token)
        """
        # Check if user exists by email
        stmt = select(Profile).where(Profile.email == email.lower())
        result = await session.execute(stmt)
        profile = result.scalars().first()
        
        # If user exists, return them with new tokens
        if profile:
            roles = await AuthService.get_user_roles(session, str(profile.id))
            access_token, refresh_token = create_tokens(
                user_id=str(profile.id),
                email=profile.email,
                roles=roles if roles else ["user"]
            )
            return profile, access_token, refresh_token
        
        # Create new user
        user_id = uuid.uuid4()
        profile = Profile(
            id=user_id,
            email=email.lower(),
            full_name=full_name,
            avatar_url=avatar_url,
            subscription_tier="free",
            access_level="basic",
            oauth_provider=provider,
            oauth_provider_id=provider_id
        )
        
        session.add(profile)
        
        # Assign 'user' role by default
        user_role = UserRole(
            id=uuid.uuid4(),
            user_id=user_id,
            role="user"
        )
        session.add(user_role)
        
        await session.flush()
        await session.commit()
        
        # Create tokens
        access_token, refresh_token = create_tokens(
            user_id=str(user_id),
            email=email.lower(),
            roles=["user"]
        )
        
        return profile, access_token, refresh_token
