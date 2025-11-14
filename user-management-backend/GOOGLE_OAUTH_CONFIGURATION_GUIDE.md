# Google OAuth Configuration Guide - Redirect URI Mismatch Fix

## Issue Identified ✅

**Error**: `Error 400: redirect_uri_mismatch`
**Message**: "Access blocked: codemurf's request is invalid"

**Root Cause**: Google Cloud Console is configured with a different redirect URI than what the backend is sending.

## Current Configuration Mismatch

### Backend Sending:
```
redirect_uri = http://localhost:8000/api/auth/google/callback
```

### Google Cloud Console Configured:
```
redirect_uri = http://localhost:3000/auth/callback  (WRONG)
```

## Solution: Update Google Cloud Console

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Select your project (likely the one using the Client ID: 37099745939-4v685b95lv9r2306l...)
3. Navigate to: **APIs & Services → Credentials**
4. Find **OAuth 2.0 Client IDs** section
5. Click on your OAuth 2.0 Client ID

### Step 2: Update Authorized Redirect URIs
1. Scroll down to **Authorized redirect URIs** section
2. **Remove** the incorrect URI: `http://localhost:3000/auth/callback`
3. **Add** the correct URI: `http://localhost:8000/api/auth/google/callback`
4. Click **Save** at the bottom

### Required Redirect URI:
```
http://localhost:8000/api/auth/google/callback
```

### Alternative: Add Both for Development
For development, you can add both URIs to be safe:
```
http://localhost:3000/auth/callback
http://localhost:8000/api/auth/google/callback
```

## Production Configuration

When deploying to production, update to:
```
https://your-domain.com/api/auth/google/callback
```

## Verification Steps

### After Updating Google Cloud Console:

1. **Test OAuth Flow**:
   ```bash
   python3 test_oauth_real_flow.py
   ```

2. **Expected Success**:
   - No more `redirect_uri_mismatch` errors
   - Backend processes callback successfully
   - Frontend receives valid tokens

3. **Check Backend Logs**:
   Look for:
   ```
   🔍 OAuth callback for google
   🔍 Callback URL: http://localhost:8000/api/auth/google/callback?code=...
   🔍 Authorization code received: 4/0Ab32j...
   🔍 Token exchange successful!
   🔍 User identified: user@cisinlabs.com
   🔍 JWT tokens created for user...
   🔍 Redirecting to: http://localhost:3000/auth/callback?access_token=...
   ```

## Current OAuth Flow (Fixed)

```
1. User clicks "Login with Google"
   ↓
2. Backend: GET /api/auth/google/login
   ↓
3. Redirect to Google with: redirect_uri=http://localhost:8000/api/auth/google/callback
   ↓
4. User authenticates with Google
   ↓
5. Google redirects to: http://localhost:8000/api/auth/google/callback?code=...
   ↓
6. Backend processes callback, exchanges code for tokens
   ↓
7. Backend redirects to frontend: http://localhost:3000/auth/callback?access_token=JWT&refresh_token=JWT&user_id=ID
   ↓
8. Frontend extracts and stores tokens
```

## Quick Fix Checklist

- [ ] Go to Google Cloud Console
- [ ] Navigate to APIs & Services → Credentials
- [ ] Find OAuth 2.0 Client ID: 37099745939-4v685b95lv9r2306l...
- [ ] Update Authorized Redirect URIs
- [ ] Add: `http://localhost:8000/api/auth/google/callback`
- [ ] Remove: `http://localhost:3000/auth/callback` (if exists)
- [ ] Save changes
- [ ] Test OAuth flow again

## Alternative Solutions

### Option 1: Use Frontend Callback (Simpler)
If you prefer to keep the Google Cloud Console as-is, revert the backend to use frontend callback:

```python
# In app/api/auth.py, change back to:
frontend_url = "http://localhost:3000"
redirect_uri = f"{frontend_url}/auth/callback"

# And in token exchange, use:
'redirect_uri': f"http://localhost:3000/auth/callback"
```

**Pros**: No need to update Google Cloud Console
**Cons**: Less secure, frontend needs to handle OAuth callback

### Option 2: Use Backend Callback (Recommended - Current Fix)
Keep the current backend configuration and update Google Cloud Console.

**Pros**: More secure, backend handles OAuth flow
**Cons**: Requires Google Cloud Console update

## Recommendation

**Use Option 2 (Backend Callback)** for better security and proper OAuth flow handling.

The current backend implementation is correct - we just need to update the Google Cloud Console to match the redirect URI.

## After Fix

Once Google Cloud Console is updated, the OAuth flow will work seamlessly:

1. ✅ No more `redirect_uri_mismatch` errors
2. ✅ Backend processes callbacks correctly
3. ✅ Frontend receives valid tokens
4. ✅ Complete OAuth authentication flow

The backend code is correct - this is just a configuration issue in the Google Cloud Console.
