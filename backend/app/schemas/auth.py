"""Authentication schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class SignUpRequest(BaseModel):
    """User sign up request schema."""
    email: EmailStr
    password: str
    full_name: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class SignInRequest(BaseModel):
    """User sign in request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    subscription_tier: str
    access_level: str
    roles: list[str]
    created_at: datetime
    oauth_provider: Optional[str] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Combined authentication response."""
    user: UserResponse
    token: TokenResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
