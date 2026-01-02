"""Authentication API routes for sign up, sign in, and token refresh."""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    SignUpRequest, SignInRequest, AuthResponse, TokenResponse,
    UserResponse, RefreshTokenRequest, ChangePasswordRequest,
    PasswordResetRequest, PasswordResetConfirm, PasswordResetResponse
)
from app.services.auth_service import AuthService
from app.services.imo_mail_service import IMOMailService
from app.services.search_limit_service import SearchLimitService
from app.api.dependencies import get_current_user
from app.models.user import Profile
from app.utils.auth import get_token_expiration_time
from app.utils.google_oauth import GoogleOAuth
from app.config import settings
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

search_limit_service = SearchLimitService()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    request: SignUpRequest,
    session: AsyncSession = Depends(get_db),
    x_session_id: Optional[str] = Header(None)
):
    """Register a new user with email and password.
    
    - **email**: User email address (must be unique)
    - **password**: Password (min 8 chars, 1 uppercase, 1 digit)
    - **full_name**: User's full name
    - **x_session_id**: (Header, optional) Guest session ID to migrate to new account
    
    Returns:
    - User profile with token information
    """
    logger.info(f"[Auth] Signup request received - x_session_id: {x_session_id or 'None'}")
    try:
        profile, access_token, refresh_token = await AuthService.sign_up(
            session=session,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        user_id = str(profile.id)
        
        # Migrate guest session to registered user account if provided
        if x_session_id:
            logger.info(f"[Auth] Signup: Migrating session {x_session_id} to user {user_id}")
            migrate_success = await search_limit_service.migrate_guest_session_to_user(
                db=session,
                session_id=x_session_id,
                user_id=user_id
            )
            if migrate_success:
                logger.info(f"[Auth] Session migration successful")
            else:
                logger.warning(f"[Auth] Session migration failed (non-fatal)")
        
        # Get user roles
        roles = await AuthService.get_user_roles(session, user_id)
        
        # Send welcome email asynchronously
        try:
            await IMOMailService.send_new_user_onboarding_email(
                db=session,
                user_email=profile.email,
                user_name=profile.full_name,
                has_trial=True,
                trial_days=7
            )
            logger.info(f"[Auth] Welcome email sent to {profile.email}")
        except Exception as email_error:
            logger.error(f"[Auth] Failed to send welcome email to {profile.email}: {email_error}")
            # Don't fail the signup if email fails
        
        user_response = UserResponse(
            id=user_id,
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
        logger.error(f"[Auth] Signup error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during sign up"
        )


@router.post("/signin", response_model=AuthResponse)
async def sign_in(
    request: SignInRequest,
    session: AsyncSession = Depends(get_db),
    x_session_id: Optional[str] = Header(None)
):
    """Authenticate user with email and password.
    
    - **email**: User email address
    - **password**: User password
    - **x_session_id**: (Header, optional) Guest session ID to migrate to existing account
    
    Returns:
    - User profile with token information
    """
    logger.info(f"[Auth] Signin request received - x_session_id: {x_session_id or 'None'}")
    try:
        profile, access_token, refresh_token = await AuthService.sign_in(
            session=session,
            email=request.email,
            password=request.password
        )
        
        user_id = str(profile.id)
        
        # Migrate guest session to registered user account if provided
        if x_session_id:
            logger.info(f"[Auth] Signin: Migrating session {x_session_id} to user {user_id}")
            migrate_success = await search_limit_service.migrate_guest_session_to_user(
                db=session,
                session_id=x_session_id,
                user_id=user_id
            )
            if migrate_success:
                logger.info(f"[Auth] Session migration successful")
            else:
                logger.warning(f"[Auth] Session migration failed (non-fatal)")
        
        # Get user roles
        roles = await AuthService.get_user_roles(session, user_id)
        
        user_response = UserResponse(
            id=user_id,
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
        logger.warning(f"[Auth] Signin validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"[Auth] Signin error: {str(e)}", exc_info=True)
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


@router.post("/forgot-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def forgot_password(
    request: PasswordResetRequest,
    session: AsyncSession = Depends(get_db)
):
    """Request a password reset link.
    
    - **email**: User email address
    
    Returns:
    - Success message (doesn't reveal if email exists for security)
    """
    try:
        logger.info(f"[Auth] Password reset requested for email: {request.email}")
        
        # Request password reset (returns token and email if user exists)
        result = await AuthService.request_password_reset(
            session=session,
            email=request.email.lower()
        )
        
        if result:
            token, user_email = result
            
            # Get user profile to get full name
            from sqlalchemy import select
            stmt = select(Profile).where(Profile.email == user_email)
            profile_result = await session.execute(stmt)
            profile = profile_result.scalars().first()
            
            if profile:
                # Send password reset email
                try:
                    await IMOMailService.send_password_reset_email(
                        db=session,
                        user_email=user_email,
                        user_name=profile.full_name,
                        reset_token=token
                    )
                    logger.info(f"[Auth] Password reset email sent to {user_email}")
                except Exception as email_error:
                    logger.error(f"[Auth] Failed to send password reset email: {email_error}")
                    # Don't fail the request even if email fails
        
        # Always return success message for security (don't reveal if email exists)
        return PasswordResetResponse(
            message="If an account exists with this email, you will receive a password reset link"
        )
        
    except Exception as e:
        logger.error(f"[Auth] Password reset request error: {str(e)}", exc_info=True)
        # Return success message anyway for security
        return PasswordResetResponse(
            message="If an account exists with this email, you will receive a password reset link"
        )


@router.post("/reset-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def reset_password(
    request: PasswordResetConfirm,
    session: AsyncSession = Depends(get_db)
):
    """Reset password using a reset token.
    
    - **token**: Password reset token from email link
    - **new_password**: New password (min 8 chars, 1 uppercase, 1 digit)
    
    Returns:
    - Success message
    """
    try:
        logger.info("[Auth] Password reset confirmation attempted")
        
        # Reset the password
        success = await AuthService.reset_password(
            session=session,
            token=request.token,
            new_password=request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        logger.info("[Auth] Password reset successful")
        return PasswordResetResponse(
            message="Password has been reset successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Auth] Password reset error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during password reset"
        )


@router.get("/verify-reset-token")
async def verify_reset_token(
    token: str = Query(...),
    session: AsyncSession = Depends(get_db)
):
    """Verify if a password reset token is valid.
    
    - **token**: Password reset token
    
    Returns:
    - Valid: True/False
    - Email: User email if valid
    """
    try:
        email = await AuthService.verify_reset_token(session, token)
        
        if email:
            return {
                "valid": True,
                "email": email
            }
        else:
            return {
                "valid": False,
                "email": None
            }
            
    except Exception as e:
        logger.error(f"[Auth] Token verification error: {str(e)}", exc_info=True)
        return {
            "valid": False,
            "email": None
        }


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
