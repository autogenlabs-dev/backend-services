# Google OAuth Fix Instructions

## 🚨 Critical Bug: Redirect URI Mismatch

The callback endpoint in `app/api/auth.py` line 319 uses the wrong port (8001 instead of 8000), causing Google's "redirect_uri_mismatch" error.

## 🔧 Apply Fix Now

### Method 1: Manual Edit

Edit `app/api/auth.py` line 319:

**FROM:**
```python
redirect_uri_for_token = "http://localhost:8001/api/auth/google/callback"  # 🚨 BUG: Should be port 8000
```

**TO:**
```python
redirect_uri_for_token = "http://localhost:8000/api/auth/google/callback"
```

### Method 2: Using sed (Linux/macOS)

```bash
sed -i 's/localhost:8001/localhost:8000/g' app/api/auth.py
```

### Method 3: Using PowerShell (Windows)

```powershell
(Get-Content app/api/auth.py) -replace 'localhost:8001', 'localhost:8000' | Set-Content app/api/auth.py
```

## 🔍 Verify Fix Applied

After applying the fix, verify the change:

```bash
grep -n "redirect_uri_for_token" app/api/auth.py
```

Should show:
```python
redirect_uri_for_token = "http://localhost:8000/api/auth/google/callback"
```

## 🧪 Test the Fix

1. **Restart backend server**
2. **Test OAuth flow:**
   - Open frontend → Click "Login with Google"
   - Should redirect to Google with `redirect_uri=http://localhost:8000/api/auth/google/callback`
   - After consent, should return to `http://localhost:8000/api/auth/google/callback?code=...`
   - Backend logs should show successful token exchange
   - Should redirect to frontend with JWT tokens

3. **Check for other port mismatches:**
   ```bash
   grep -r "localhost:8001" . || echo "No more port 8001 references found"
   ```

## ✅ Expected Success Indicators

- No "redirect_uri_mismatch" error in backend logs
- Successful token exchange with Google
- JWT tokens created and passed to frontend
- User successfully logged in

## 🔄 If Still Failing

1. Check Google Cloud Console redirect URIs match exactly:
   - Development: `http://localhost:8000/api/auth/google/callback`
   - Production: `https://api.codemurf.com/api/auth/google/callback`

2. Verify environment variables:
   ```bash
   echo "GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID"
   echo "GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET:0:10}..." # Show first 10 chars
   echo "ENVIRONMENT: $ENVIRONMENT"
   ```

3. Check backend logs for exact error messages

4. Test with curl to isolate the issue:
   ```bash
   curl -X POST https://oauth2.googleapis.com/token \
     -d "code=TEST_CODE" \
     -d "client_id=$GOOGLE_CLIENT_ID" \
     -d "client_secret=$GOOGLE_CLIENT_SECRET" \
     -d "redirect_uri=http://localhost:8000/api/auth/google/callback" \
     -d "grant_type=authorization_code"
   ```

## 📋 Complete Flow After Fix

1. User clicks "Login with Google" → Frontend redirects to backend
2. Backend redirects to Google OAuth with correct callback URI (port 8000)
3. User authenticates with Google → Google redirects to backend callback
4. Backend exchanges code for tokens using matching redirect URI (port 8000) ✅
5. Backend creates JWT tokens and redirects to frontend
6. Frontend stores tokens and authenticates user

## 🔐 Security Note

Consider implementing secure token transfer instead of URL parameters:
- Set HttpOnly, Secure cookies from backend
- Or use short-lived codes exchanged for tokens on frontend

Apply this fix now to resolve the redirect_uri_mismatch error!