"""Authentication API routes for sign up, sign in, and token refresh."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    SignUpRequest, SignInRequest, AuthResponse, TokenResponse,
    UserResponse, RefreshTokenRequest, ChangePasswordRequest
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import Profile
from app.utils.auth import get_token_expiration_time
from app.utils.google_oauth import GoogleOAuth
from app.config import settings
import secrets

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    request: SignUpRequest,
    session: AsyncSession = Depends(get_db)
):
    """Register a new user with email and password.
    
    - **email**: User email address (must be unique)
    - **password**: Password (min 8 chars, 1 uppercase, 1 digit)
    - **full_name**: User's full name
    
    Returns:
    - User profile with token information
    """
    try:
        profile, access_token, refresh_token = await AuthService.sign_up(
            session=session,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        # Get user roles
        roles = await AuthService.get_user_roles(session, str(profile.id))
        
        user_response = UserResponse(
            id=str(profile.id),
            email=profile.email,
            full_name=profile.full_name,
            avatar_url=profile.avatar_url,
            subscription_tier=profile.subscription_tier,
            access_level=profile.access_level,
            roles=roles,
            created_at=profile.created_at
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_EXPIRATION_HOURS * 3600
        )
        
        return AuthResponse(user=user_response, token=token_response)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during sign up"
        )


@router.post("/signin", response_model=AuthResponse)
async def sign_in(
    request: SignInRequest,
    session: AsyncSession = Depends(get_db)
):
    """Authenticate user with email and password.
    
    - **email**: User email address
    - **password**: User password
    
    Returns:
    - User profile with token information
    """
    try:
        profile, access_token, refresh_token = await AuthService.sign_in(
            session=session,
            email=request.email,
            password=request.password
        )
        
        # Get user roles
        roles = await AuthService.get_user_roles(session, str(profile.id))
        
        user_response = UserResponse(
            id=str(profile.id),
            email=profile.email,
            full_name=profile.full_name,
            avatar_url=profile.avatar_url,
            subscription_tier=profile.subscription_tier,
            access_level=profile.access_level,
            roles=roles,
            created_at=profile.created_at
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_EXPIRATION_HOURS * 3600
        )
        
        return AuthResponse(user=user_response, token=token_response)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during sign in"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token from previous authentication
    
    Returns:
    - New access and refresh tokens
    """
    tokens = await AuthService.refresh_access_token(session, request.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    access_token, new_refresh_token = tokens
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Profile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get current authenticated user information.
    
    Returns:
    - Current user profile
    """
    roles = await AuthService.get_user_roles(session, str(current_user.id))
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        subscription_tier=current_user.subscription_tier,
        access_level=current_user.access_level,
        roles=roles,
        created_at=current_user.created_at
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    current_user: Profile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Change password for current user.
    
    - **current_password**: User's current password
    - **new_password**: New password (min 8 chars, 1 uppercase, 1 digit)
    
    Returns:
    - Success message
    """
    success = await AuthService.change_password(
        session=session,
        user_id=str(current_user.id),
        current_password=request.current_password,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password. Incorrect current password."
        )
    
    return {"message": "Password changed successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: Profile = Depends(get_current_user)):
    """Logout current user.
    
    Note: JWT tokens are stateless. To logout, client should discard the token.
    This endpoint is for API consistency.
    
    Returns:
    - Success message
    """
    return {"message": "Logged out successfully"}


@router.get("/google/login")
async def google_login():
    """Get Google OAuth login URL.
    
    Returns:
    - URL to redirect user to for Google authentication
    """
    state = secrets.token_urlsafe(32)
    auth_url = GoogleOAuth.get_authorization_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/google/callback", response_model=AuthResponse)
async def google_callback(
    code: str = Query(...),
    session: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback.
    
    Args:
    - code: Authorization code from Google
    
    Returns:
    - User profile with token information
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code"
        )
    
    try:
        # Get user info from Google
        oauth_data = await GoogleOAuth.authenticate_user(code)
        
        if not oauth_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google"
            )
        
        user_info = oauth_data.get("user", {})
        google_id = user_info.get("id")
        email = user_info.get("email")
        full_name = user_info.get("name")
        picture = user_info.get("picture")
        
        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google user information"
            )
        
        # Get or create user
        profile, access_token, refresh_token = await AuthService.get_or_create_oauth_user(
            session=session,
            email=email,
            full_name=full_name or email.split("@")[0],
            provider="google",
            provider_id=google_id,
            avatar_url=picture
        )
        
        # Get user roles
        roles = await AuthService.get_user_roles(session, str(profile.id))
        
        user_response = UserResponse(
            id=str(profile.id),
            email=profile.email,
            full_name=profile.full_name,
            avatar_url=profile.avatar_url,
            subscription_tier=profile.subscription_tier,
            access_level=profile.access_level,
            roles=roles,
            created_at=profile.created_at,
            oauth_provider=profile.oauth_provider
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_EXPIRATION_HOURS * 3600
        )
        
        return AuthResponse(user=user_response, token=token_response)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in Google callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during Google authentication"
        )
