# Backend Authentication Integration Guide

## Overview

Complete authentication system integrated between backend FastAPI and React frontend with JWT tokens, password hashing, and role-based access control.

## Frontend Components Created/Updated

### 1. **Auth API Client** (`frontend/src/integrations/auth-api.ts`)

API client for all authentication endpoints:

```typescript
// Sign up new user
await authAPI.signUp({
  email: 'user@example.com',
  password: 'SecurePass123',
  full_name: 'John Doe'
});

// Sign in with credentials
await authAPI.signIn({
  email: 'user@example.com',
  password: 'SecurePass123'
});

// Refresh access token
await authAPI.refreshToken(refreshToken);

// Get current user
await authAPI.getCurrentUser(accessToken);

// Change password
await authAPI.changePassword(accessToken, {
  current_password: 'OldPass123',
  new_password: 'NewPass123'
});

// Logout
await authAPI.logout(accessToken);
```

### 2. **Auth Context** (`frontend/src/contexts/AuthContext.tsx`)

React Context for managing global authentication state:

```typescript
interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  signUp: (data: SignUpRequest) => Promise<void>;
  signIn: (data: SignInRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<boolean>;
  changePassword: (current: string, new: string) => Promise<void>;
}
```

**Features:**
- Automatic token persistence to localStorage
- Token expiration handling with automatic refresh
- Fallback to refresh token if access token expires
- Automatic cleanup on logout

### 3. **useAuth Hook** (`frontend/src/hooks/useAuth.tsx`)

Convenient hook to access auth context:

```typescript
const { user, isAuthenticated, signIn, signUp, signOut, accessToken } = useAuth();
```

### 4. **AuthForm Component** (`frontend/src/components/auth/AuthForm.tsx`)

Updated to use real API calls:

**Sign In Tab:**
- Email and password validation
- Real API calls to `/api/v1/auth/signin`
- Automatic redirect on success
- Error handling with toast notifications

**Sign Up Tab:**
- Full name, email, password validation
- Password strength requirements (8+ chars, 1 uppercase, 1 digit)
- Password confirmation matching
- Real API calls to `/api/v1/auth/signup`
- Auto-assignment of 'user' role

### 5. **UserMenu Component** (`frontend/src/components/auth/UserMenu.tsx`)

Enhanced user menu with:

**User Information:**
- Display full name or email
- Show subscription tier
- User initials avatar

**Menu Items:**
- Admin Dashboard (for admin users only)
- Profile Settings
- Liked Products
- Security Settings
- Sign Out

### 6. **ProtectedRoute Component** (`frontend/src/components/ProtectedRoute.tsx`)

Route protection with role-based access:

```typescript
// Basic protection (requires authentication)
<ProtectedRoute>
  <ProfilePage />
</ProtectedRoute>

// Role-based protection
<ProtectedRoute requiredRoles={['admin']}>
  <AdminDashboard />
</ProtectedRoute>

// Multiple roles (any match)
<ProtectedRoute requiredRoles={['admin', 'moderator']}>
  <AdminPanel />
</ProtectedRoute>
```

### 7. **App.tsx Integration**

AuthProvider wraps entire app:

```typescript
<Router>
  <AuthProvider>
    {/* All routes have access to auth context */}
    <Layout>
      <Routes>...</Routes>
    </Layout>
  </AuthProvider>
</Router>
```

## Backend Changes

### 1. **Authentication Routes** (`backend/app/api/routes/auth.py`)

Six endpoints implemented:

```
POST   /api/v1/auth/signup           → Create new user account
POST   /api/v1/auth/signin           → Sign in with credentials
POST   /api/v1/auth/refresh          → Refresh access token
GET    /api/v1/auth/me               → Get current user (protected)
POST   /api/v1/auth/change-password  → Change password (protected)
POST   /api/v1/auth/logout           → Logout (protected, stateless)
```

### 2. **Dependencies** (`backend/app/api/dependencies.py`)

Authentication dependency functions:

```python
# Extract and validate JWT token
async def get_current_user(credentials, session) -> Profile

# Optional authentication
async def get_optional_user(credentials, session) -> Optional[Profile]

# Role-based access control
def require_role(*allowed_roles) -> Callable
```

### 3. **Database Integration**

Migration created: `backend/alembic/versions/003_add_password_hash.py`

- Adds `password_hash` column to Profile table
- Non-nullable after migration completes
- Existing users get empty string default

## Testing the Integration

### 1. **Start Backend Server**

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. **Start Frontend Development Server**

```bash
cd frontend
npm run dev
```

### 3. **Test Authentication Flow**

**Sign Up:**
1. Navigate to `/auth?tab=signup`
2. Enter full name, email, password
3. Verify password requirements displayed
4. Click "Create Account"
5. Should redirect to home page
6. User menu should show user's full name

**Sign In:**
1. Navigate to `/auth`
2. Enter email and password
3. Click "Sign In"
4. Should redirect to home page
5. User menu should be populated

**Protected Routes:**
1. Sign out from user menu
2. Navigate to `/profile`
3. Should redirect to `/auth`
4. Sign in again
5. Should access protected route

**Token Refresh:**
1. Sign in to get tokens
2. Wait for access token to expire (or manually test)
3. Make request to protected endpoint
4. Should automatically refresh and retry

### 4. **Using curl/Postman**

**Sign Up:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

**Sign In:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

**Get Current User (Protected):**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Refresh Token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<REFRESH_TOKEN>"}'
```

## Token Storage

Tokens stored in localStorage with structure:

```typescript
// AUTH_TOKENS key
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expiresAt": 1234567890000  // Timestamp in milliseconds
}

// AUTH_USER key
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": null,
  "subscription_tier": "free",
  "access_level": "basic",
  "roles": ["user"],
  "created_at": "2025-01-23T10:00:00"
}
```

## Configuration

Backend JWT settings in `backend/app/config.py`:

```python
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
JWT_REFRESH_EXPIRATION_DAYS = 7
PASSWORD_MIN_LENGTH = 8
```

**IMPORTANT: Change `JWT_SECRET_KEY` in production!**

Environment variables:

```bash
# .env file
JWT_SECRET_KEY=your-secure-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=7
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db
```

## Frontend API Configuration

Backend URL configured in `frontend/src/config/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

**Environment variable:**
```bash
# .env.local in frontend
VITE_API_URL=http://localhost:8000
```

## Dependencies Added

**Backend:**
- PyJWT==2.8.1 (JWT token handling)
- passlib==1.7.4 (Password utilities)
- bcrypt==4.1.1 (Password hashing)

**Frontend:**
- Already has all necessary dependencies (fetch API built-in)

## API Response Formats

### Success Responses

**Sign Up/Sign In (201/200):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": null,
    "subscription_tier": "free",
    "access_level": "basic",
    "roles": ["user"],
    "created_at": "2025-01-23T10:00:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Get Current User (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": null,
  "subscription_tier": "free",
  "access_level": "basic",
  "roles": ["user"],
  "created_at": "2025-01-23T10:00:00"
}
```

### Error Responses

**Invalid Credentials (401):**
```json
{
  "detail": "Invalid email or password"
}
```

**Email Already Registered (400):**
```json
{
  "detail": "Email already registered"
}
```

**Missing Fields (422):**
```json
{
  "detail": "Validation error"
}
```

## Future Enhancements

1. **Email Verification**
   - Send verification email on signup
   - Require verification before full access

2. **Password Reset**
   - Email-based password reset flow
   - Reset token validation

3. **Two-Factor Authentication**
   - TOTP/SMS-based 2FA
   - Backup codes

4. **Session Management**
   - Token blacklist on logout
   - Device tracking
   - Session revocation

5. **OAuth Integration**
   - Google OAuth
   - GitHub OAuth
   - Apple OAuth

6. **Admin Management**
   - Admin role assignment UI
   - User permission management
   - Admin audit logs

## Troubleshooting

### CORS Errors

If getting CORS errors, ensure backend CORS is configured:

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Token Expired Errors

If getting 401 errors:
1. Check `expiresAt` in localStorage
2. Verify refresh token is valid
3. Check backend time synchronization

### Database Migration Issues

If migration fails:

```bash
cd backend
# Check migration status
alembic current

# Downgrade if needed
alembic downgrade -1

# Upgrade again
alembic upgrade head
```

## Files Modified

**Frontend:**
- ✅ `src/integrations/auth-api.ts` (NEW)
- ✅ `src/contexts/AuthContext.tsx` (NEW)
- ✅ `src/hooks/useAuth.tsx` (UPDATED)
- ✅ `src/components/auth/AuthForm.tsx` (UPDATED)
- ✅ `src/components/auth/UserMenu.tsx` (UPDATED)
- ✅ `src/components/ProtectedRoute.tsx` (UPDATED)
- ✅ `src/App.tsx` (UPDATED)

**Backend:**
- ✅ `app/config.py` (UPDATED - JWT settings)
- ✅ `app/schemas/auth.py` (NEW)
- ✅ `app/utils/auth.py` (NEW)
- ✅ `app/services/auth_service.py` (NEW)
- ✅ `app/models/user.py` (UPDATED - password_hash)
- ✅ `app/api/routes/auth.py` (NEW)
- ✅ `app/api/dependencies.py` (UPDATED)
- ✅ `app/api/__init__.py` (UPDATED)
- ✅ `alembic/versions/003_add_password_hash.py` (NEW)
- ✅ `requirements.txt` (UPDATED)

## Next Steps

1. Run database migration: `alembic upgrade head`
2. Start backend server
3. Start frontend dev server
4. Test signup/signin flow
5. Test protected routes
6. Test token refresh
7. Deploy to production with secure JWT_SECRET_KEY
