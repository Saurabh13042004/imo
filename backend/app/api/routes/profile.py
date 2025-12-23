"""Profile management API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.database import get_db
from app.models.user import Profile
from app.api.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.utils.auth import hash_password, verify_password
from app.schemas.auth import UserResponse
import os
import uuid

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.get("/me", response_model=UserResponse)
async def get_profile(
    current_user: Profile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get current user profile."""
    roles = await AuthService.get_user_roles(session, str(current_user.id))
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        subscription_tier=current_user.subscription_tier,
        access_level=current_user.access_level,
        roles=roles,
        created_at=current_user.created_at,
        oauth_provider=current_user.oauth_provider
    )


@router.put("/update", response_model=UserResponse)
async def update_profile(
    full_name: str = None,
    current_user: Profile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Update user profile information."""
    try:
        if full_name:
            current_user.full_name = full_name
        
        session.add(current_user)
        await session.flush()
        await session.commit()
        
        roles = await AuthService.get_user_roles(session, str(current_user.id))
        
        return UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.full_name,
            avatar_url=current_user.avatar_url,
            subscription_tier=current_user.subscription_tier,
            access_level=current_user.access_level,
            roles=roles,
            created_at=current_user.created_at,
            oauth_provider=current_user.oauth_provider
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )


@router.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: Profile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Upload user profile photo."""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "static/uploads/avatars"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Update user avatar URL
        avatar_url = f"/uploads/avatars/{unique_filename}"
        current_user.avatar_url = avatar_url
        
        session.add(current_user)
        await session.flush()
        await session.commit()
        
        return {
            "message": "Photo uploaded successfully",
            "avatar_url": avatar_url
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to upload photo"
        )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: Profile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Change user password."""
    try:
        # Check if user has a password (not OAuth-only user)
        if not current_user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change password for OAuth-only accounts. Set a password first."
            )
        
        # Verify current password
        if not verify_password(current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.password_hash = hash_password(new_password)
        session.add(current_user)
        await session.flush()
        await session.commit()
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )


@router.post("/disconnect-oauth")
async def disconnect_oauth(
    current_user: Profile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Disconnect OAuth provider from account."""
    try:
        # Check if user has a password (can't disconnect if no password)
        if not current_user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot disconnect OAuth without a password. Set a password first."
            )
        
        # Remove OAuth provider info
        current_user.oauth_provider = None
        current_user.oauth_provider_id = None
        
        session.add(current_user)
        await session.flush()
        await session.commit()
        
        return {"message": "OAuth provider disconnected successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to disconnect OAuth provider"
        )


@router.post("/connect-oauth")
async def connect_oauth(
    provider: str,
    provider_id: str,
    current_user: Profile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Connect OAuth provider to existing account."""
    try:
        current_user.oauth_provider = provider
        current_user.oauth_provider_id = provider_id
        
        session.add(current_user)
        await session.flush()
        await session.commit()
        
        return {"message": f"{provider.capitalize()} connected successfully"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect OAuth provider"
        )
