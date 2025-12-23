"""Google OAuth 2.0 utilities for authentication."""

import json
import httpx
from typing import Optional, Dict, Any
from app.config import settings


class GoogleOAuth:
    """Google OAuth 2.0 handler."""
    
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    @classmethod
    def get_authorization_url(cls, state: str) -> str:
        """Generate Google OAuth authorization URL.
        
        Args:
            state: State parameter for CSRF protection
            
        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
        }
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{cls.GOOGLE_AUTH_URL}?{query_string}"
    
    @classmethod
    async def exchange_code_for_token(cls, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Token response with access_token, id_token, etc.
        """
        payload = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    cls.GOOGLE_TOKEN_URL,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    @classmethod
    async def get_user_info(cls, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google using access token.
        
        Args:
            access_token: Google access token
            
        Returns:
            User information (id, email, name, picture, etc.)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    cls.GOOGLE_USERINFO_URL,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    @classmethod
    async def authenticate_user(cls, code: str) -> Optional[Dict[str, Any]]:
        """Complete Google OAuth flow: exchange code for token and get user info.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            User information with tokens
        """
        # Exchange code for tokens
        token_response = await cls.exchange_code_for_token(code)
        if not token_response:
            return None
        
        # Get user info
        access_token = token_response.get("access_token")
        user_info = await cls.get_user_info(access_token)
        
        if not user_info:
            return None
        
        # Combine user info with token info
        return {
            "user": user_info,
            "tokens": token_response,
        }
