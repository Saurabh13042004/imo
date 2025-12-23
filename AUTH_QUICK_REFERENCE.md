# Authentication & Access Control - Quick Reference

## Starting the Application

### Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## Using Authentication

### Sign Up
```typescript
import { useAuth } from '@/hooks/useAuth';

const { signUp } = useAuth();

await signUp({
  email: 'user@example.com',
  password: 'SecurePass123',
  full_name: 'John Doe'
});
```

### Sign In
```typescript
const { signIn } = useAuth();

await signIn({
  email: 'user@example.com',
  password: 'SecurePass123'
});
```

### Check Authentication
```typescript
const { user, isAuthenticated, loading } = useAuth();

if (loading) return <div>Loading...</div>;
if (!isAuthenticated) return <Navigate to="/auth" />;

return <div>Welcome {user?.full_name}</div>;
```

### Sign Out
```typescript
const { signOut } = useAuth();

await signOut();
```

## Using Access Control

### Check Guest Searches
```typescript
import { 
  getRemainingGuestSearches,
  hasGuestSearchesRemaining 
} from '@/utils/accessControl';

const remaining = getRemainingGuestSearches(); // 0, 1, 2, etc.
const canSearch = hasGuestSearchesRemaining(); // true/false
```

### Record Guest Search
```typescript
import { incrementGuestSearchCount } from '@/utils/accessControl';

// After guest performs search
if (!user) {
  incrementGuestSearchCount();
}
```

### Get Display Limits
```typescript
import { getProductDisplayLimit } from '@/utils/accessControl';

// Guest: 5 products
const limit = getProductDisplayLimit(false);

// Free-tier: 10 products
const limit = getProductDisplayLimit(true, 'free');

// Paid: 50 products
const limit = getProductDisplayLimit(true, 'pro');

const displayProducts = products.slice(0, limit);
```

## Protected Routes

### Basic Protection
```typescript
import { ProtectedRoute } from '@/components/ProtectedRoute';

<ProtectedRoute>
  <ProfilePage />
</ProtectedRoute>
```

### Admin Only
```typescript
<ProtectedRoute requiredRoles={['admin']}>
  <AdminDashboard />
</ProtectedRoute>
```

## Environment Variables

### Frontend (.env.local)
```bash
VITE_API_URL=http://localhost:8000
VITE_GUEST_FREE_SEARCHES=1
VITE_GUEST_PRODUCT_DISPLAY_LIMIT=5
VITE_FREE_TIER_PRODUCT_DISPLAY_LIMIT=10
VITE_PAID_TIER_PRODUCT_DISPLAY_LIMIT=50
```

### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=7
DEBUG=False
```

## API Examples

### Sign Up
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### Sign In
```bash
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Get Current User
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<REFRESH_TOKEN>"}'
```

### Change Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123",
    "new_password": "NewPass123"
  }'
```

## Testing Guest Limits

### Open Incognito Window
```
http://localhost:5173/search
```

### Perform Search
1. Enter search query
2. Click search
3. See "1/1 free searches" banner
4. View products (limited to 5)

### Exhaust Searches
1. Try to search again
2. See "Free searches exhausted" message
3. Click "Sign In to Continue"
4. After login, limits removed

## Resetting Guest Search Count

### Browser Console
```javascript
localStorage.removeItem('imo_guest_search_count');
localStorage.removeItem('imo_guest_search_date');
// Now guest has 1 free search again
```

## Common Issues & Solutions

### Issue: "Invalid or expired token"
**Solution:** Token expired, automatic refresh should handle it. If not:
```javascript
// Force logout and re-login
localStorage.removeItem('auth_tokens');
localStorage.removeItem('auth_user');
window.location.href = '/auth';
```

### Issue: Guest search count not working
**Solution:** Check environment variables
```bash
# Verify in console
import { getAccessControlConfig } from '@/utils/accessControl';
console.log(getAccessControlConfig());
```

### Issue: CORS error
**Solution:** Verify backend CORS configuration
```python
# In app/main.py, check CORSMiddleware settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Database migration fails
**Solution:** Reset and retry
```bash
cd backend
alembic downgrade -1  # Undo last migration
alembic upgrade head   # Reapply all
```

## Useful Commands

### Backend
```bash
# Run server
python -m uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Check migration status
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest
```

### Frontend
```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Format code
npm run format
```

## Documentation Links

- **Full Auth Guide:** See `AUTHENTICATION_INTEGRATION_GUIDE.md`
- **Access Control Guide:** See `TIERED_ACCESS_CONTROL.md`
- **Implementation Details:** See `IMPLEMENTATION_COMPLETE.md`
- **API Documentation:** Auto-generated at `http://localhost:8000/docs`
