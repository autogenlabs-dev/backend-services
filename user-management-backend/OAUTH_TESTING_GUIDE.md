# Google OAuth Testing Guide

## 🚀 Quick Start Commands

### Start Backend Server

```bash
# Navigate to backend directory
cd user-management-backend

# Start the server (choose one method)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# OR if using requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend Server

```bash
# Navigate to frontend directory (if separate)
cd /path/to/your/frontend

# Start Next.js development server
npm run dev

# OR if using specific port
npm run dev -- -p 3000
```

## 🧪 Step-by-Step Testing Process

### 1. Verify Backend is Running

Open browser and navigate to:
```
http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "..."}
```

### 2. Verify Frontend is Running

Open browser and navigate to:
```
http://localhost:3000
```

Should see your frontend application.

### 3. Test OAuth Login Flow

1. **Open frontend login page**
   - Navigate to `http://localhost:3000/auth` or your login page
   - Click "Login with Google" button

2. **Verify Google Redirect**
   - Browser should redirect to Google OAuth
   - Check the URL in address bar - should contain:
     ```
     https://accounts.google.com/o/oauth2/auth?client_id=...&redirect_uri=http://localhost:8000/api/auth/google/callback&response_type=code&scope=openid+email+profile&state=...
     ```
   - **Important**: Verify `redirect_uri` parameter shows `http://localhost:8000/api/auth/google/callback` (port 8000, not 8001)

3. **Complete Google Authentication**
   - Sign in with your Google account
   - Grant permissions when prompted
   - Google should redirect back to your backend

4. **Check Backend Callback Processing**
   - Watch backend terminal for debug messages:
     ```
     🔍 OAuth callback for google
     🔍 Callback URL: http://localhost:8000/api/auth/google/callback?code=...&state=...
     🔍 Authorization code received: ...
     🔍 Exchanging code for token at: https://oauth2.googleapis.com/token
     🔍 Token exchange successful!
     🔍 Getting user info from: https://www.googleapis.com/oauth2/v2/userinfo
     🔍 User info retrieved: your.email@gmail.com
     🔍 User identified: your.email@gmail.com (ID: ...)
     🔍 JWT tokens created for user ...
     🔍 Redirecting to: http://localhost:3000/auth/callback?access_token=...&refresh_token=...&user_id=...
     ```

5. **Verify Frontend Token Handling**
   - Frontend should receive the redirect with tokens
   - Check browser URL after redirect: should be `http://localhost:3000/auth/callback?access_token=...`
   - Frontend should extract and store tokens
   - User should be logged in and redirected to dashboard

## 🔍 Monitoring Backend Logs

Keep your backend terminal visible during testing. Look for these key messages:

### ✅ Success Indicators
- `🔍 OAuth callback for google`
- `🔍 Authorization code received: ...`
- `🔍 Token exchange successful!`
- `🔍 User info retrieved: your.email@gmail.com`
- `🔍 JWT tokens created for user ...`
- `🔍 Redirecting to: http://localhost:3000/auth/callback?...`

### ❌ Error Indicators
- `🔍 Token exchange failed: 400 - {"error":"redirect_uri_mismatch",...}`
- `🔍 OAuth callback error: Token exchange failed: ...`
- `🔍 No authorization code found in callback`
- `🔍 OAuth error returned: access_denied`

## 🛠️ Common Issues and Solutions

### Issue: Redirect URI Mismatch
**Error**: `{"error":"redirect_uri_mismatch","error_description":"Bad Request"}`

**Cause**: Backend callback URL doesn't match what's registered in Google Cloud Console

**Solution**:
1. Verify the fix was applied correctly (port 8000, not 8001)
2. Check Google Cloud Console authorized redirect URIs:
   - Development: `http://localhost:8000/api/auth/google/callback`
   - Production: `https://api.codemurf.com/api/auth/google/callback`

### Issue: CORS Errors
**Error**: Browser blocks redirect with CORS error

**Solution**:
1. Verify frontend URL (`http://localhost:3000`) is in backend CORS origins
2. Check backend CORS configuration in `app/config.py`

### Issue: Missing Environment Variables
**Error**: `OAuth provider google is not configured`

**Solution**:
1. Check your `.env` file contains:
   ```
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```
2. Verify environment variables are loaded correctly

## 🧪 Automated Testing Script

Create this test script to automate the testing process:

```bash
#!/bin/bash
# oauth_test.sh

echo "🚀 Starting Google OAuth Test"
echo "=========================="

# Test 1: Check backend health
echo "1. Testing backend health..."
curl -s http://localhost:8000/health | jq '.'
echo ""

# Test 2: Test OAuth login initiation
echo "2. Testing OAuth login initiation..."
LOGIN_RESPONSE=$(curl -s -I http://localhost:8000/api/auth/google/login | grep -i location | cut -d' ' -f2)
echo "Redirect URL: $LOGIN_RESPONSE"
echo ""

# Test 3: Check providers endpoint
echo "3. Testing OAuth providers..."
curl -s http://localhost:8000/api/auth/providers | jq '.'
echo ""

echo "✅ Testing complete!"
echo "=========================="
echo "📋 Manual testing required for complete flow verification"
echo "1. Open http://localhost:3000 in browser"
echo "2. Click 'Login with Google'"
echo "3. Complete Google authentication"
echo "4. Check backend terminal for success messages"
```

Make it executable:
```bash
chmod +x oauth_test.sh
./oauth_test.sh
```

## 📱 Browser Developer Tools Testing

1. **Open Developer Tools** (F12) before starting OAuth flow
2. **Go to Network Tab**
3. **Clear Network Log**
4. **Initiate OAuth Login**
5. **Monitor Network Requests**:
   - Should see request to `/api/auth/google/login` (302 redirect)
   - Should see redirect to Google OAuth
   - After Google auth, should see request to `/api/auth/google/callback`
   - Check callback request contains authorization code
   - Should see token exchange request to Google
   - Should see user info request to Google
   - Should see final redirect to frontend

## 📊 Expected Success Flow

1. Frontend → Backend: `GET /api/auth/google/login`
2. Backend → Google: Redirect to OAuth (302)
3. User → Google: Authenticate and grant permission
4. Google → Backend: `GET /api/auth/google/callback?code=...`
5. Backend → Google: `POST /oauth2.googleapis.com/token` (exchange code)
6. Google → Backend: Token response
7. Backend → Google: `GET /oauth2/v2/userinfo` (get user info)
8. Backend → Frontend: Redirect with JWT tokens
9. Frontend → Backend: API calls with Bearer token

## 🔐 Security Verification

After successful login, verify JWT tokens work:

```bash
# Test with the access token returned
ACCESS_TOKEN="your-token-here"
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     http://localhost:8000/api/auth/me
```

Expected response:
```json
{
  "id": "...",
  "email": "your.email@gmail.com",
  "is_active": true,
  ...
}
```

## 📝 Test Results Template

Use this template to document your test results:

```markdown
# Google OAuth Test Results

## Environment
- Backend URL: http://localhost:8000
- Frontend URL: http://localhost:3000
- Date/Time: 2025-11-06 11:30 AM
- Google Client ID: [REDACTED]

## Test Results

### Backend Health Check
- Status: ✅ Pass
- Response Time: 150ms

### OAuth Login Initiation
- Status: ✅ Pass
- Redirect URL: Correct (port 8000)
- Google OAuth URL: Correct

### OAuth Callback Processing
- Status: ✅ Pass
- Token Exchange: Success
- User Info Retrieved: Success
- JWT Tokens Created: Success
- Frontend Redirect: Success

### Frontend Token Handling
- Status: ✅ Pass
- Tokens Stored: Success
- User Logged In: Success

### API Authentication Test
- Status: ✅ Pass
- JWT Verification: Success
- Protected Resource Access: Success

## Issues Found

### Issue 1: [None]
- Description: [No issues found]
- Resolution: [N/A]

## Summary

- Overall Status: ✅ SUCCESS
- Google OAuth Flow: Working Correctly
- Recommendation: Ready for production deployment

## Screenshots

[Attach screenshots of key steps if needed]
```

## 🎯 Production Deployment Checklist

Before deploying to production, verify:

- [ ] Google Cloud Console has production redirect URI: `https://api.codemurf.com/api/auth/google/callback`
- [ ] Environment variables set: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- [ ] Production CORS includes: `https://codemurf.com`
- [ ] HTTPS certificates valid for production domain
- [ ] Load balancer/proxy configuration preserves OAuth headers
- [ ] Session storage uses secure, HttpOnly cookies in production
- [ ] JWT secret key is strong and unique to production
- [ ] Error logging is appropriate for production (no sensitive data)

Run this testing guide after applying the redirect URI fix to verify your Google OAuth flow works correctly!