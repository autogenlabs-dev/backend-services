# Google OAuth Debugging Guide

This document provides comprehensive technical details for debugging Google OAuth login flow issues in the Python + Next.js setup.

## 🚨 Critical Bug Found

**Redirect URI Mismatch** in `app/api/auth.py:319`:
- Login endpoint uses: `http://localhost:8000/api/auth/google/callback`
- Callback endpoint uses: `http://localhost:8001/api/auth/google/callback` (port 8001!)

This will cause Google to reject the token exchange with "redirect_uri_mismatch" error.

## 🔧 Immediate Fix Required

Change line 319 in `app/api/auth.py`:
```python
# FROM:
redirect_uri_for_token = "http://localhost:8001/api/auth/google/callback"

# TO:
redirect_uri_for_token = "http://localhost:8000/api/auth/google/callback"
```

### Apply Fix Now

```diff
-        if getattr(settings, 'environment', 'development') == 'development':
-            redirect_uri_for_token = "http://localhost:8001/api/auth/google/callback"  # 🚨 BUG: Should be port 8000
+        if getattr(settings, 'environment', 'development') == 'development':
+            redirect_uri_for_token = "http://localhost:8000/api/auth/google/callback"
         else:
             redirect_uri_for_token = "https://api.codemurf.com/api/auth/google/callback"
```

After changing this, restart your backend server.

## 🔁 Quick Search (Find Other Bad References)

Run this in your repo root to ensure no other code uses port 8001 by mistake:

```bash
# Linux / macOS
grep -R "localhost:8001" -n || true

# or show all occurrences of "/api/auth/google/callback"
grep -R "/api/auth/google/callback" -n || true
```

Fix any other mismatching entries you find.

## 🧪 How to Test (Step-by-Step)

1. Restart backend
2. Open browser → frontend → click Login with Google
3. Watch browser address bar: it should redirect to accounts.google.com and show `redirect_uri` param set to `http://localhost:8000/api/auth/google/callback`
4. After consenting, browser should return to `http://localhost:8000/api/auth/google/callback?code=...&state=....`
5. Backend logs should show:
   ```
   Exchanging code for token at: https://oauth2.googleapis.com/token
   Token exchange successful!
   User info retrieved: <email>
   JWT tokens created...
   ```
6. Frontend should receive redirect `http://localhost:3000/auth/callback?access_token=...` (if you still use URL params) and then use access token for API calls

If something fails, copy the exact backend log/error (e.g., `400 - {"error":"redirect_uri_mismatch",...}`) and paste it for debugging.

## 🔐 Security & Reliability Recommendations

### Do Not Pass Tokens in URL
URLs are logged and can leak tokens. Instead:
- Return a short-lived code from backend → frontend, or
- Set cookies from backend (HttpOnly, Secure, SameSite) and let frontend read session state via API

If changing now is too big, plan to migrate ASAP.

### Use Same Redirect URI in Three Places
- Your code (login & callback)
- Google Cloud Console (Authorized redirect URIs)
- Any env/config used by CI/deploy

### Validate State Parameter
Ensure you verify state in the callback to prevent CSRF.

### Prefer Authlib's Authorize/Token Helpers
If you manually exchange tokens, ensure parameters, headers, and Content-Type match Google docs. Authlib handles a lot of subtle details for you.

### Rotate Client Secret
Rotate client secret if it was accidentally logged or committed.

### Log Minimally
Avoid printing full tokens. Keep logs to first/last few chars only if you must.

## ✅ Production Checklist

- [ ] Ensure production BACKEND_URL and Google Cloud redirect URI are `https://api.codemurf.com/api/auth/google/callback`
- [ ] Ensure environment variable `environment = production` on prod boxes
- [ ] Ensure HTTPS for production endpoints
- [ ] Confirm CORS allowlist includes `https://codemurf.com`
- [ ] Confirm cookie/security settings if switching to HttpOnly cookies

## 🛠️ Extras: Sample curl to Simulate Token Exchange

If you want to reproduce the exchange failure to see the exact error body from Google (useful before and after fix), you can run:

```bash
curl -X POST https://oauth2.googleapis.com/token \
  -d code="CODE_FROM_CALLBACK" \
  -d client_id="YOUR_CLIENT_ID" \
  -d client_secret="YOUR_CLIENT_SECRET" \
  -d redirect_uri="http://localhost:8000/api/auth/google/callback" \
  -d grant_type="authorization_code"
```

A `redirect_uri_mismatch` will return a 400 JSON you can inspect.

---

## 1️⃣ OAuth Route Code

### `/api/auth/google/login` Endpoint

```python
# From app/api/auth.py:234-271
@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth login with a provider."""
    if provider not in ["openrouter", "google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth provider"
        )
    
    config = get_provider_config(provider)
    if not config or not config.get("client_id"):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"OAuth provider {provider} is not configured"
        )
    
    try:
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"OAuth provider {provider} is not available"
            )
        # Use correct redirect URI that matches Google OAuth configuration
        # For development, we need to use a URL that matches what's registered in Google
        if getattr(settings, 'environment', 'development') == 'development':
            # Development - use backend URL directly since Google can't reach localhost:3000
            redirect_uri = "http://localhost:8000/api/auth/google/callback"
        else:
            # Production - use the registered production callback
            redirect_uri = "https://api.codemurf.com/api/auth/google/callback"
        
        return await client.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth login: {str(e)}"
        )
```

### `/api/auth/google/callback` Endpoint

```python
# From app/api/auth.py:274-451
@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Handle OAuth callback and create user session."""
    if provider not in ["openrouter", "google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth provider"
        )
    
    try:
        # Debug: Log the callback URL and parameters
        print(f"🔍 OAuth callback for {provider}")
        print(f"🔍 Callback URL: {request.url}")
        
        # Extract authorization code directly from URL for development
        from urllib.parse import parse_qs
        parsed_url = str(request.url)
        query_params = parse_qs(parsed_url.split('?')[1] if '?' in parsed_url else '')
        
        code = query_params.get('code', [None])[0]
        error = query_params.get('error', [None])[0]
        
        if error:
            print(f"🔍 OAuth error returned: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth error: {error}"
            )
        
        if not code:
            print("🔍 No authorization code found in callback")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No authorization code received"
            )
        
        print(f"🔍 Authorization code received: {code[:20]}...")
        
        # Exchange code for token directly (bypassing authlib for development)
        # Use same redirect URI that was used in authorize step
        if getattr(settings, 'environment', 'development') == 'development':
            redirect_uri_for_token = "http://localhost:8001/api/auth/google/callback"  # 🚨 BUG: Should be port 8000
        else:
            redirect_uri_for_token = "https://api.codemurf.com/api/auth/google/callback"
            
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri_for_token,
            'client_id': getattr(settings, f'{provider}_client_id', None),
            'client_secret': getattr(settings, f'{provider}_client_secret', None)
        }
        
        import httpx
        config = get_provider_config(provider)
        token_endpoint = config.get("token_endpoint")
        
        if not token_endpoint:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Token endpoint not configured for {provider}"
            )
        
        print(f"🔍 Exchanging code for token at: {token_endpoint}")
        
        async with httpx.AsyncClient() as http_client:
            token_response = await http_client.post(token_endpoint, data=token_data)
            
            if token_response.status_code != 200:
                print(f"🔍 Token exchange failed: {token_response.status_code} - {token_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Token exchange failed: {token_response.text}"
                )
            
            token = token_response.json()
            print("🔍 Token exchange successful!")
        
        # Get user info from provider
        userinfo_endpoint = config.get("userinfo_endpoint")
        access_token = token.get('access_token')
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No access token in response"
            )
        
        user_data = {}
        if userinfo_endpoint:
            print(f"🔍 Getting user info from: {userinfo_endpoint}")
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with httpx.AsyncClient() as http_client:
                user_response = await http_client.get(userinfo_endpoint, headers=headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    print(f"🔍 User info retrieved: {user_data.get('email', 'No email')}")
                else:
                    print(f"🔍 Failed to get user info: {user_response.status_code}")
        
        # Extract user information
        if provider == "github":
            # GitHub requires a separate call to get email
            email_url = "https://api.github.com/user/emails"
            headers = {'Authorization': f'Bearer {access_token}'}
            async with httpx.AsyncClient() as http_client:
                email_response = await http_client.get(email_url, headers=headers)
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next((email for email in emails if email.get("primary")), None)
                    email = primary_email.get("email") if primary_email else user_data.get("email")
                else:
                    email = user_data.get("email")
        else:
            email = user_data.get("email")

        provider_user_id = user_data.get("id") or user_data.get("sub")
        
        if not email or not provider_user_id:
            print(f"🔍 Missing user data - email: {email}, provider_user_id: {provider_user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract user information from OAuth provider"
            )
        
        print(f"🔍 User identified: {email} (ID: {provider_user_id})")
        
        # Get or create user
        user = await get_or_create_user_by_oauth(
            db=db,
            provider_name=provider,
            provider_user_id=str(provider_user_id),
            email=email
        )
        
        # Update last login
        if user and user.id:
            await update_user_last_login(db, user.id)
        
        # Create JWT tokens
        access_token_jwt = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        refresh_token_jwt = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        print(f"🔍 JWT tokens created for user {user.id}")
        
        # Return redirect URL for frontend to handle
        if getattr(settings, 'environment', 'development') == 'development':
            frontend_url = "http://localhost:3000/auth/callback"
        else:
            frontend_url = "https://codemurf.com/auth/callback"
        redirect_params = f"?access_token={access_token_jwt}&refresh_token={refresh_token_jwt}&user_id={user.id}"
        
        print(f"🔍 Redirecting to: {frontend_url}{redirect_params[:50]}...")
        
        # Directly redirect to frontend with tokens in URL params
        return RedirectResponse(url=f"{frontend_url}{redirect_params}")
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"🔍 OAuth callback error: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )
```

### Helper Functions

```python
# From app/auth/oauth.py:76-83
def get_oauth_client(provider: str):
    """Get OAuth client for a specific provider."""
    return oauth.create_client(provider)

def get_provider_config(provider: str) -> Dict[str, Any]:
    """Get configuration for a specific OAuth provider."""
    return OAUTH_PROVIDERS.get(provider, {})

# From app/services/user_service.py:165-237
async def get_or_create_user_by_oauth(
    db: AsyncIOMotorDatabase,
    provider_name: str,
    provider_user_id: str,
    email: str,
    name: Optional[str] = None
) -> User:
    """Get or create user from OAuth provider information."""
    # Get provider - Assuming OAuthProvider is also a Beanie Document
    provider = await OAuthProvider.find_one(OAuthProvider.name == provider_name)
    if not provider:
        # If provider doesn't exist, create it for now for simplicity
        from ..auth.oauth import OAUTH_PROVIDERS
        provider_config = OAUTH_PROVIDERS.get(provider_name, {})
        display_name = provider_config.get("display_name", provider_name.title())
        
        provider = OAuthProvider(
            name=provider_name,
            display_name=display_name
        )
        await provider.insert()

    # Check if OAuth account exists
    oauth_account = await UserOAuthAccount.find_one(
        UserOAuthAccount.provider_id == provider.id,
        UserOAuthAccount.provider_user_id == provider_user_id
    )

    if oauth_account:
        # Update last used time
        oauth_account.last_used_at = datetime.now(timezone.utc)
        await oauth_account.save()
        # Need to fetch the user document explicitly
        user = await User.get(oauth_account.user_id)
        # Also update user's last login time
        if user:
            await update_user_last_login(db, user.id)
        return user

    # Check if user exists by email
    user = await get_user_by_email(db, email)
    if not user:
        # Create new user
        user = User(
            email=email,
            name=name or email.split('@')[0], # Use provided name or email prefix
            is_active=True,
            subscription="free", # Default subscription
            tokens_remaining=10000, # Default tokens
            tokens_used=0,
            monthly_limit=10000, # Default monthly limit
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_login_at=datetime.now(timezone.utc), # Set last login on creation
            full_name=name # Use provided name as full_name
        )
        await user.insert()

    # Create OAuth account link
    oauth_account = UserOAuthAccount(
        user_id=user.id,
        provider_id=provider.id,
        provider_user_id=provider_user_id,
        email=email,
        last_used_at=datetime.now(timezone.utc)
    )
    await oauth_account.insert()

    # Need to return user document
    return user
```

---

## 2️⃣ Token Functions

```python
# From app/auth/jwt.py:41-61
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

# From app/auth/jwt.py:64-70
def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None

# From app/auth/jwt.py:86-121
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Any = Depends(get_database)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
            
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Convert user_id to UUID if it's a string
        try:
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
        except (ValueError, TypeError):
            raise credentials_exception
              
        # Get user from database
        user = await User.get(user_id)
        
        if user is None:
            raise credentials_exception
            
        return user
            
    except JWTError:
        raise credentials_exception
```

---

## 3️⃣ Environment & Config

```python
# From app/config.py:64-73
# OAuth
oauth_providers: List[str] = ["openrouter", "google", "github"]

# OAuth Client Credentials
openrouter_client_id: str = "your_openrouter_client_id"
openrouter_client_secret: str = "your_openrouter_client_secret"
google_client_id: str = "your_google_client_id"
google_client_secret: str = "your_google_client_secret"
github_client_id: str = "your_github_client_id"
github_client_secret: str = "your_github_client_secret"

# From app/config.py:47-52
# Production URLs
production_frontend_url: str = "https://codemurf.com"
production_backend_url: str = "https://api.codemurf.com"

# CORS
backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080", "https://codemurf.com", "https://www.codemurf.com"]
```

### Expected Environment Values

```bash
GOOGLE_CLIENT_ID=xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxx
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Redirect URI Configuration

**Development:**
- Registered in Google Cloud Console: `http://localhost:8000/api/auth/google/callback`
- Login endpoint uses: `http://localhost:8000/api/auth/google/callback` ✅
- Callback endpoint uses: `http://localhost:8001/api/auth/google/callback` ❌ (BUG!)

**Production:**
- Registered in Google Cloud Console: `https://api.codemurf.com/api/auth/google/callback`
- Login endpoint uses: `https://api.codemurf.com/api/auth/google/callback` ✅
- Callback endpoint uses: `https://api.codemurf.com/api/auth/google/callback` ✅

---

## 4️⃣ Backend Logs

### Expected logs during login initiation:

```
🔍 OAuth callback for google
🔍 Callback URL: http://localhost:8000/api/auth/google/callback?code=xxxx&state=xxxx
🔍 Authorization code received: xxxx...
🔍 Exchanging code for token at: https://oauth2.googleapis.com/token
🔍 Token exchange successful!
🔍 Getting user info from: https://www.googleapis.com/oauth2/v2/userinfo
🔍 User info retrieved: user@example.com
🔍 User identified: user@example.com (ID: 123456789)
🔍 JWT tokens created for user 60f1b2c3d4e5f6a7b8c9d0e1f2a3b4c5
🔍 Redirecting to: http://localhost:3000/auth/callback?access_token=xxxx&refresh_token=xxxx&user_id=60f1b2c3d4e5f6a7b8c9d0e1f2a3b4c5...
```

### Expected logs during callback error:

```
🔍 Token exchange failed: 400 - {"error":"redirect_uri_mismatch","error_description":"Bad Request"}
🔍 OAuth callback error: Token exchange failed: {"error":"redirect_uri_mismatch","error_description":"Bad Request"}
```

---

## 5️⃣ Frontend Flow

### Typical Next.js Login Component:

```javascript
// Example Next.js component that triggers Google OAuth
const LoginWithGoogle = () => {
  const handleGoogleLogin = () => {
    // Redirect to backend OAuth login
    window.location.href = 'http://localhost:8000/api/auth/google/login';
  };

  return (
    <button onClick={handleGoogleLogin}>
      Login with Google
    </button>
  );
};
```

### Expected Google Redirect URL:

```
https://accounts.google.com/o/oauth2/auth?client_id=xxxx.apps.googleusercontent.com&redirect_uri=http://localhost:8000/api/auth/google/callback&response_type=code&scope=openid+email+profile&state=xxxx
```

### Expected Callback URL after Google login:

```
http://localhost:8000/api/auth/google/callback?code=4/0AX4XfWh...&state=xxxx
```

---

## 6️⃣ Error Behavior

### Most Likely Issues:

1. **Redirect URI Mismatch** (Critical bug found):
   - Login uses port 8000
   - Callback uses port 8001
   - Google rejects token exchange

2. **Missing Environment Variables**:
   - Google client ID/secret not set
   - OAuth provider not configured

3. **CORS Issues**:
   - Frontend URL not in CORS origins
   - Browser blocks redirect

4. **Token Exchange Failure**:
   - Invalid client credentials
   - Network connectivity issues

### Debugging Steps:

1. **Fix redirect URI mismatch** in callback endpoint (line 319)
2. Check environment variables are properly set
3. Verify Google Cloud Console has correct redirect URI
4. Monitor backend console logs during OAuth flow
5. Check browser network tab for failed requests

### Common Error Messages and Solutions:

| Error | Cause | Solution |
|--------|--------|----------|
| `redirect_uri_mismatch` | Port mismatch between login and callback | Fix line 319 in auth.py |
| `invalid_client` | Wrong client ID/secret | Check environment variables |
| `access_denied` | User denied permission | User needs to grant access |
| CORS errors | Frontend URL not allowed | Add to CORS origins |

---

## 🎯 Quick Fix Checklist

- [ ] Fix redirect URI mismatch in `app/api/auth.py:319`
- [ ] Verify Google Cloud Console redirect URI
- [ ] Check environment variables are set
- [ ] Test OAuth flow with browser dev tools
- [ ] Monitor backend console logs
- [ ] Verify frontend URL in CORS origins

---

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI OAuth Documentation](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)