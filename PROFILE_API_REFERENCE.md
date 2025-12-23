# Profile API Reference

## Base URL
```
http://localhost:8000/api/v1/profile
```

All endpoints require authentication via `Authorization: Bearer {access_token}` header.

---

## Endpoints

### 1. Get Current User Profile

**GET** `/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "/uploads/avatars/abc123.jpg",
  "subscription_tier": "free",
  "access_level": "basic",
  "roles": ["user"],
  "created_at": "2025-12-23T06:00:00",
  "oauth_provider": "google"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User not found

---

### 2. Update User Profile

**PUT** `/update`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "full_name": "Jane Doe"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "avatar_url": "/uploads/avatars/abc123.jpg",
  "subscription_tier": "free",
  "access_level": "basic",
  "roles": ["user"],
  "created_at": "2025-12-23T06:00:00",
  "oauth_provider": "google"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Invalid or missing token

---

### 3. Upload Profile Photo

**POST** `/upload-photo`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <binary image file>
```

**Supported Formats:** JPG, PNG, GIF, WebP  
**Max Size:** 10MB

**Response (200 OK):**
```json
{
  "message": "Photo uploaded successfully",
  "avatar_url": "/uploads/avatars/550e8400-e29b-41d4-a716-446655440000.jpg"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid file or upload failed
- `401 Unauthorized`: Invalid or missing token
- `413 Payload Too Large`: File exceeds max size

---

### 4. Change Password

**POST** `/change-password`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "current_password": "OldPassword123",
  "new_password": "NewPassword456"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 digit

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request`: 
  - `"Cannot change password for OAuth-only accounts. Set a password first."`
  - `"Password too weak. Please create a stronger password."`
- `401 Unauthorized`: Current password is incorrect
- `422 Unprocessable Entity`: Validation error

**Example Error Response:**
```json
{
  "detail": "Current password is incorrect"
}
```

---

### 5. Disconnect OAuth Provider

**POST** `/disconnect-oauth`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```
(empty)
```

**Response (200 OK):**
```json
{
  "message": "OAuth provider disconnected successfully"
}
```

**Error Responses:**
- `400 Bad Request`: 
  - `"Cannot disconnect OAuth without a password. Set a password first."`
- `401 Unauthorized`: Invalid or missing token

**Notes:**
- Prevents account lockout by requiring a password
- User can still sign in with email/password after disconnection

---

### 6. Connect OAuth Provider

**POST** `/connect-oauth`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "provider": "google",
  "provider_id": "118159236971238918236"
}
```

**Supported Providers:** google, facebook, github, etc.

**Response (200 OK):**
```json
{
  "message": "Google connected successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Failed to connect provider
- `401 Unauthorized`: Invalid or missing token

---

## Authentication

All endpoints require a valid JWT access token.

### Token Header Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Placement
Tokens can be obtained from:
- `/api/v1/auth/signup` - User registration
- `/api/v1/auth/signin` - User login
- `/api/v1/auth/google/callback` - Google OAuth
- `/api/v1/auth/refresh` - Token refresh

---

## Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success - Request completed successfully |
| `201` | Created - Resource created successfully |
| `400` | Bad Request - Invalid parameters or validation error |
| `401` | Unauthorized - Missing or invalid authentication |
| `404` | Not Found - Resource doesn't exist |
| `422` | Unprocessable Entity - Validation error |
| `500` | Internal Server Error - Server error occurred |

---

## Rate Limiting

Currently no rate limiting implemented. Future versions may include:
- IP-based rate limiting
- User-based rate limiting
- Endpoint-specific limits

---

## CORS

All endpoints allow CORS requests from any origin during development.

**Production Configuration:** Update CORS settings in `app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## Examples

### cURL Example

**Get Profile:**
```bash
curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Update Profile:**
```bash
curl -X PUT http://localhost:8000/api/v1/profile/update \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "New Name"}'
```

**Upload Photo:**
```bash
curl -X POST http://localhost:8000/api/v1/profile/upload-photo \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/photo.jpg"
```

**Change Password:**
```bash
curl -X POST http://localhost:8000/api/v1/profile/change-password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123",
    "new_password": "NewPass456"
  }'
```

---

### JavaScript/Fetch Example

**Get Profile:**
```javascript
const response = await fetch('/api/v1/profile/me', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  }
});
const data = await response.json();
console.log(data);
```

**Upload Photo:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/v1/profile/upload-photo', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData
});
const data = await response.json();
console.log(data.avatar_url);
```

---

## Error Handling

Always check response status and handle errors:

```javascript
try {
  const response = await fetch('/api/v1/profile/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.detail);
    return;
  }

  const user = await response.json();
  console.log('Success:', user);
} catch (error) {
  console.error('Network error:', error);
}
```

---

## Changelog

### Version 1.0 (2025-12-23)
- Initial profile API implementation
- All endpoints functional
- Complete documentation

---

**Last Updated:** December 23, 2025  
**API Version:** 1.0
