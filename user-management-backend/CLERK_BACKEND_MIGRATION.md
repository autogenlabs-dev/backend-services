# CLERK AUTHENTICATION MIGRATION GUIDE

## 🎯 Overview

The backend has been updated to support **Clerk authentication** from the frontend while maintaining backward compatibility with:
- Legacy JWT tokens
- VS Code extension API keys
- Old OAuth flows (for migration period)

## 🔑 Key Changes

### 1. **User Model Updated**
Added new fields to support Clerk integration:
- `clerk_id` - Clerk user identifier (indexed for fast lookups)
- `first_name` - User's first name from Clerk
- `last_name` - User's last name from Clerk
- `email_verified` - Email verification status from Clerk

### 2. **New Authentication Module**
Created `app/auth/clerk_auth.py` with:
- `verify_clerk_token()` - Verifies Clerk JWT tokens
- `get_or_create_user_from_clerk()` - Syncs Clerk users with backend
- `get_current_user_clerk()` - Main Clerk authentication dependency

### 3. **Unified Authentication**
Updated `app/auth/unified_auth.py` to support all auth methods:
```python
# Priority order:
1. X-API-Key header (VS Code extension)
2. Bearer API key (VS Code extension fallback)
3. Bearer Clerk JWT (Frontend web app) ⭐ NEW
4. Bearer Legacy JWT (Old systems)
```

### 4. **Configuration Updates**
Added to `app/config.py`:
```python
clerk_secret_key: str
clerk_publishable_key: str
clerk_frontend_api: str
clerk_jwks_url: str
```

### 5. **Main Application Updates**
In `app/main.py`:
- Commented out old OAuth client registration
- Added note about Clerk handling frontend auth
- Session middleware kept for backward compatibility

## 📋 Environment Variables Required

### Backend `.env` or `.env.production`:
```bash
# Clerk Authentication (NEW)
CLERK_SECRET_KEY=sk_test_FtxbYvBnDrtJ7ajXTT0N8ehm3iQxNK1DYaCOY1jEhu
CLERK_PUBLISHABLE_KEY=pk_test_YXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2JA
CLERK_FRONTEND_API=apt-clam-53.clerk.accounts.dev
CLERK_JWKS_URL=https://apt-clam-53.clerk.accounts.dev/.well-known/jwks.json

# Legacy (keep for backward compatibility during migration)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend `.env.local`:
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2JA
CLERK_SECRET_KEY=sk_test_FtxbYvBnDrtJ7ajXTT0N8ehm3iQxNK1DYaCOY1jEhu
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔄 Authentication Flows

### Frontend Web App (Clerk)
```
1. User signs in via Clerk on frontend
2. Clerk issues JWT session token
3. Frontend includes token in API requests: Authorization: Bearer <clerk_jwt>
4. Backend verifies Clerk JWT
5. Backend creates/updates user in MongoDB
6. API request proceeds with authenticated user
```

### VS Code Extension (API Key)
```
1. Extension uses stored API key
2. Extension includes: X-API-Key: sk_xxxx
3. Backend validates API key
4. API request proceeds with authenticated user
```

### Legacy Systems (JWT)
```
1. System uses old JWT tokens
2. Request includes: Authorization: Bearer <legacy_jwt>
3. Backend tries Clerk verification (fails)
4. Backend falls back to legacy JWT verification
5. API request proceeds with authenticated user
```

## 🛠️ Usage Examples

### Protect a Route with Unified Auth
```python
from fastapi import APIRouter, Depends
from app.auth.unified_auth import get_current_user_unified
from app.models.user import User

router = APIRouter()

@router.get("/api/protected")
async def protected_route(
    current_user: User = Depends(get_current_user_unified)
):
    """This route accepts Clerk JWT, API keys, or legacy JWT"""
    return {
        "message": "Success",
        "user": current_user.to_dict()
    }
```

### Optional Authentication
```python
from app.auth.unified_auth import get_optional_current_user_unified

@router.get("/api/public-or-protected")
async def optional_auth_route(
    current_user: Optional[User] = Depends(get_optional_current_user_unified)
):
    """This route works with or without authentication"""
    if current_user:
        return {"message": "Authenticated", "user_id": str(current_user.id)}
    return {"message": "Anonymous access"}
```

### Clerk-Only Authentication
```python
from app.auth.clerk_auth import get_current_user_clerk

@router.get("/api/clerk-only")
async def clerk_only_route(
    current_user: User = Depends(get_current_user_clerk)
):
    """This route ONLY accepts Clerk JWT tokens"""
    return {"message": "Clerk authenticated", "clerk_id": current_user.clerk_id}
```

## 🧪 Testing the Integration

### 1. Test Frontend Web App Authentication
```bash
# Start backend
cd user-management-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend
cd ../Autogenlabs-Web-App
npm run dev

# Visit http://localhost:3000
# Sign in with Clerk
# Check browser DevTools Network tab for API calls with Clerk JWT
```

### 2. Test VS Code Extension Authentication
```bash
# Extension should use X-API-Key header
curl -H "X-API-Key: sk_your_api_key" http://localhost:8000/api/me
```

### 3. Test Legacy JWT Authentication
```bash
# Old JWT tokens should still work
curl -H "Authorization: Bearer <old_jwt_token>" http://localhost:8000/api/me
```

## 📊 Migration Checklist

- [x] Add Clerk authentication module (`clerk_auth.py`)
- [x] Update User model with Clerk fields
- [x] Update unified authentication to support Clerk
- [x] Comment out old OAuth registration
- [x] Add Clerk configuration to settings
- [x] Update environment variables
- [ ] Deploy backend with new code
- [ ] Deploy frontend with Clerk integration
- [ ] Test all authentication methods
- [ ] Monitor logs for auth failures
- [ ] Gradually deprecate old OAuth endpoints

## 🚨 Important Notes

### Security Considerations
1. **Token Verification**: Currently using unverified Clerk tokens for development. **MUST** implement proper JWKS verification for production.
2. **User Sync**: Users are automatically created/synced from Clerk tokens. Monitor for duplicate accounts.
3. **API Keys**: VS Code extension API keys remain unchanged.

### Backward Compatibility
- All existing endpoints continue to work
- Old OAuth code is commented out but not removed
- Legacy JWT tokens still accepted
- API keys for extensions unchanged

### Production Deployment

#### Update Production .env:
```bash
# Use production Clerk keys
CLERK_SECRET_KEY=sk_live_...
CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_FRONTEND_API=your-production-domain.clerk.accounts.dev
```

#### Enable JWKS Verification:
In `app/auth/clerk_auth.py`, uncomment:
```python
# In production, add proper signature verification:
jwks = await get_clerk_jwks()
payload = jwt.decode(token, jwks, algorithms=["RS256"], issuer=CLERK_ISSUER)
```

#### Install Required Dependencies:
```bash
pip install httpx python-jose[cryptography]
```

## 🐛 Troubleshooting

### "Could not validate credentials" Error
- Check if Clerk token is being sent in Authorization header
- Verify Clerk secret key in environment variables
- Check backend logs for specific error messages

### User Not Found After Clerk Login
- Check if email from Clerk matches existing user
- Look for `clerk_id` field in user document
- Check MongoDB logs for user creation

### API Key Authentication Not Working
- Ensure API key is sent in X-API-Key header
- Verify API key exists in database
- Check API key hasn't expired

## 📝 Code Comments Added

All old OAuth code has been marked with:
```python
# COMMENTED OUT - OLD OAUTH: <reason>
```

This makes it easy to:
1. Find old authentication code
2. Understand why it was commented
3. Remove it completely after migration period

## 🎉 Benefits of This Migration

1. ✅ **Simplified Frontend Auth**: Clerk handles all OAuth providers
2. ✅ **Better UX**: Faster sign-in with Clerk's optimized UI
3. ✅ **Enhanced Security**: Clerk's built-in security features
4. ✅ **Backward Compatible**: Old systems continue to work
5. ✅ **Easy Maintenance**: Less OAuth code to maintain
6. ✅ **Unified User Management**: One source of truth for users

## 🔗 Related Documentation

- Frontend Clerk Integration: `C:\Users\Asus\Desktop\Autogenlabs-Web-App\CLERK_INTEGRATION_COMPLETE.md`
- Clerk Dashboard: https://dashboard.clerk.com/
- Backend API Docs: http://localhost:8000/docs
