"""Quick test script to verify authentication system integration."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_imports():
    """Test that all authentication modules import correctly."""
    try:
        print("Testing imports...")
        
        # Import config
        from app.config import settings
        print("✓ Config imported successfully")
        
        # Import schemas
        from app.schemas.auth import (
            SignUpRequest, SignInRequest, TokenResponse, 
            UserResponse, AuthResponse, RefreshTokenRequest, ChangePasswordRequest
        )
        print("✓ Auth schemas imported successfully")
        
        # Import utils
        from app.utils.auth import (
            hash_password, verify_password, create_tokens, 
            decode_token, get_token_expiration_time
        )
        print("✓ Auth utilities imported successfully")
        
        # Import service
        from app.services.auth_service import AuthService
        print("✓ Auth service imported successfully")
        
        # Import routes
        from app.api.routes.auth import router
        print("✓ Auth router imported successfully")
        
        # Import dependencies
        from app.api.dependencies import (
            get_current_user, get_optional_user, security
        )
        print("✓ Auth dependencies imported successfully")
        
        # Import models
        from app.models.user import Profile, UserRole
        print("✓ User models imported successfully")
        
        print("\n✅ All imports successful!")
        
        # Test password hashing
        print("\nTesting password hashing...")
        test_password = "TestPassword123"
        hashed = hash_password(test_password)
        verified = verify_password(test_password, hashed)
        assert verified, "Password verification failed"
        print("✓ Password hashing works correctly")
        
        # Test token creation
        print("\nTesting token creation...")
        access_token, refresh_token = create_tokens(
            user_id="test-user-123",
            email="test@example.com",
            roles=["user"]
        )
        assert access_token, "Access token not created"
        assert refresh_token, "Refresh token not created"
        print("✓ Token creation works correctly")
        
        # Test token decoding
        print("\nTesting token decoding...")
        decoded = decode_token(access_token)
        assert decoded, "Token decoding failed"
        assert decoded.get("user_id") == "test-user-123"
        assert decoded.get("type") == "access"
        print("✓ Token decoding works correctly")
        
        print("\n✅ All tests passed! Authentication system is ready.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_imports())
    sys.exit(0 if success else 1)
