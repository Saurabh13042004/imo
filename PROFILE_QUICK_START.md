# Profile Feature - Quick Start Guide

## 🎯 Access Profile Page

### Frontend URL
```
http://localhost:3000/profile
```

### Requirements
- Must be logged in
- Valid JWT access token in localStorage
- Browser cookies enabled

---

## 📋 Navigation Flow

```
Auth Page (/auth)
    ↓
    Sign In / Sign Up / Google OAuth
    ↓
Homepage (/)
    ↓
    Click "Profile" in navigation
    ↓
Profile Page (/profile)  ← YOU ARE HERE
    ↓
    4 Tabs Available:
    1. Personal Info
    2. Photo Upload
    3. Security
    4. Connected Apps
```

---

## 📑 Profile Page Tabs

### Tab 1: Personal Information
**Location:** First tab (default)

**Features:**
- View full name
- Edit full name
- View email (read-only)
- View account creation date
- Update button

**Steps:**
1. Edit "Full Name" field
2. Click "Update Profile"
3. Toast notification confirms success
4. Profile updates immediately

---

### Tab 2: Photo Upload
**Location:** Second tab

**Features:**
- Current photo display
- Drag-drop upload area
- Click to upload
- Image preview
- File validation
- Upload button

**Steps:**
1. Click upload area or drag file
2. Select an image (JPG, PNG, GIF)
3. Preview appears below
4. Click "Upload Photo"
5. Toast notification on success
6. Avatar updates across site

---

### Tab 3: Security
**Location:** Third tab

**Features:**
- Current password field
- New password field
- Confirm password field
- Password strength indicator
- Requirements display
- Change button

**Steps:**
1. Enter current password
2. Enter new password (8+ chars, 1 uppercase, 1 digit)
3. Confirm new password
4. Click "Change Password"
5. Fields clear on success
6. Toast confirmation

---

### Tab 4: Connected Apps
**Location:** Fourth tab

**Features:**
- Google connection status
- Connect button (if not connected)
- Disconnect button (if connected)
- Connection explanation

**To Connect Google:**
1. Click "Connect" button
2. Redirected to Google login
3. Select your Google account
4. Grant permissions
5. Redirected back to profile
6. Status shows "Connected ✓"

**To Disconnect Google:**
1. Click "Disconnect" button
2. Confirm in dialog
3. Connection removed
4. Status shows "Not connected"
5. Can still sign in with email/password

---

## 🔑 User Data Fields

All displayed in Personal tab:

| Field | Type | Editable | Display |
|-------|------|----------|---------|
| Full Name | Text | ✏️ Yes | Editable input |
| Email | Text | 🔒 No | Read-only |
| Avatar | Image | ✏️ Yes | Photo tab |
| Plan | Select | 🔒 No | Badge |
| Access Level | Select | 🔒 No | Badge |
| Created Date | Date | 🔒 No | Read-only |
| OAuth Provider | Text | ✏️ Via Tab 4 | Connected Apps |

---

## 🔐 Password Requirements

When changing password:
- **Minimum length:** 8 characters
- **Uppercase:** At least 1 (A-Z)
- **Digit:** At least 1 (0-9)
- **Special chars:** Not required but accepted

**Examples:**
- ✅ `SecurePass123`
- ✅ `MyPassword456`
- ✅ `Admin@2024`
- ❌ `password123` (no uppercase)
- ❌ `Password` (no digit)
- ❌ `Pass1` (too short)

---

## 📸 Photo Upload Details

### Supported Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

### Size Limits
- Maximum: 10 MB
- Recommended: 1-5 MB
- Aspect ratio: Any (will be displayed as-is)

### Storage
- Server stores at: `static/uploads/avatars/`
- Unique filename: `{uuid}.{extension}`
- Public URL: `http://localhost:8000/uploads/avatars/{uuid}.jpg`

### Preview
- Preview shown before upload
- Black border indicates preview mode
- Primary border indicates after upload

---

## 🔄 OAuth (Google) Flow

### What is OAuth?
OAuth allows signing in using your Google account instead of remembering a password.

### Benefits
- One-click sign in
- No password to remember
- Auto-fill profile data
- Secure authentication

### Connection Process

**Step 1: Click Connect**
- On "Connected Apps" tab
- Click "Connect" button next to Google

**Step 2: Google Consent**
- Browser redirects to Google login
- Select your Google account
- Grant IMO permission to access:
  - Email address
  - Name
  - Profile picture

**Step 3: Redirect Back**
- Automatically redirected to profile page
- Connection status updates to "Connected ✓"
- Avatar may be updated from Google picture

**Step 4: Sign In Options**
After connecting, you can sign in via:
- Email + Password (traditional)
- Google account (new option)

### Disconnection Process

**Why Disconnect?**
- Remove Google access
- Switch to email-only login
- Privacy preference
- Security reason

**Before Disconnecting:**
- ⚠️ You must have a password set
- ⚠️ You'll use email+password to sign in after
- ✅ Google won't have access anymore

**Steps:**
1. Go to "Connected Apps" tab
2. Click "Disconnect" (red button)
3. Confirm in popup
4. Status changes to "Not connected"
5. Use email+password next time

---

## 📤 Logout

**Location:** Top-right of profile header

**Steps:**
1. Click "Logout" button
2. Tokens cleared from storage
3. Redirected to auth page (/auth)
4. Session ends

**After Logout:**
- All local authentication cleared
- Must sign in again to access profile
- OAuth connections preserved

---

## ⚠️ Important Notes

### Account Security
- Never share your password
- Use strong passwords (8+ chars, mixed case, digits)
- Logout on public computers
- Update password regularly

### OAuth & Passwords
- If only OAuth connected, set a password for safety
- Password required to disconnect OAuth
- This prevents account lockout

### File Storage
- Uploaded photos stored permanently
- Accessible via unique URL
- Can be changed anytime
- Old photos remain on server

### Token Expiration
- Access token: 24 hours (default)
- Refresh token: Used to get new access token
- Auto-logout when token expires
- Page redirects to auth on token error

---

## 🆘 Troubleshooting

### Profile Won't Load
**Issue:** Page shows "Profile not found"
- **Solution:** Check if logged in, refresh page, re-login

### Photo Upload Failed
**Issue:** Error when uploading image
- **Solutions:**
  - Check file size (max 10MB)
  - Check file format (JPG, PNG, GIF)
  - Check internet connection
  - Try different browser

### Password Change Failed
**Issue:** "Current password is incorrect"
- **Solution:** Verify your current password, try again

### Can't Disconnect Google
**Issue:** "Cannot disconnect without password"
- **Solution:** Set a password first, then disconnect

### OAuth Connect Failed
**Issue:** Stuck on Google login or redirect fails
- **Solutions:**
  - Clear browser cache
  - Try incognito mode
  - Check cookies enabled
  - Disable browser extensions

### Session Expired
**Issue:** "Failed to load profile" suddenly
- **Solution:** Logout and sign in again

---

## 💡 Tips & Tricks

### Password Recovery
- Use "Reset Password" on auth page
- Check email for reset link
- Can't reset? Contact support

### Change Email
- Not available in profile
- Email is permanent account identifier
- Contact support if email wrong

### Delete Account
- Not yet implemented
- Coming in future updates
- Contact support for data deletion

### Privacy
- Profile data visible to you only
- Photos stored on server
- OAuth data not shared with third parties

---

## 🎨 Responsive Design

### Desktop (1024px+)
- All tabs visible side-by-side
- Forms display with full width
- Avatar large
- All content visible

### Tablet (768px - 1023px)
- Tabs stack if needed
- Responsive form layout
- Avatar medium size
- Scrollable content

### Mobile (< 768px)
- Tabs stack vertically
- Forms full width
- Avatar medium
- Touch-friendly buttons
- Scrollable content
- Optimized spacing

---

## 📱 Mobile Considerations

- Tap to select photos (file picker)
- Drag-drop may not work on mobile
- Use browser back button carefully
- Landscape/portrait both supported
- Toast notifications positioned for mobile

---

## 🔗 Related Pages

- **Auth Page:** `/auth` - Sign in, sign up
- **Google Callback:** `/auth/callback` - OAuth redirect
- **Home Page:** `/` - Main dashboard
- **API Docs:** `http://localhost:8000/docs` - API documentation

---

## 📊 Data You Control

**Can Edit:**
- ✏️ Full name
- ✏️ Profile photo
- ✏️ Password
- ✏️ OAuth connections

**Cannot Edit (Contact Support):**
- 🔒 Email address
- 🔒 Subscription tier
- 🔒 Access level
- 🔒 Account creation date

**Can View:**
- 👁️ Current settings
- 👁️ Account info
- 👁️ Connected apps
- 👁️ Subscription details

---

## 🚀 Next Steps

After setting up profile:
1. Upload a profile photo
2. Set a strong password
3. Connect your Google account (optional)
4. Explore other features
5. Manage your search unlocks

---

## ❓ FAQ

**Q: Can I change my email?**
A: Not currently. Contact support for email changes.

**Q: What happens to my photo if I delete account?**
A: Photos are deleted with account (when feature added).

**Q: Is my password secure?**
A: Yes, stored with bcrypt hashing. Never shared.

**Q: Can I have multiple OAuth accounts?**
A: Currently only Google. More providers coming soon.

**Q: Do you sell my data?**
A: No, data is private and only used for your account.

---

## 📞 Support

**Having Issues?**
- Check troubleshooting section above
- Contact: support@example.com
- Issues page: GitHub issues
- Chat: In-app support (coming soon)

---

**Last Updated:** December 23, 2025  
**Version:** 1.0
