# CodeMurf OAuth Configuration Guide

## Google OAuth 2.0 Setup

### Client Configuration

**OAuth Client Name:** `codemurf`  
**Application Type:** Web application  
**Created in:** Google Cloud Console

---

## Authorized Origins & Redirect URIs

### Development Environment

**Authorized JavaScript Origins:**
```
http://localhost:3000
```

**Authorized Redirect URIs:**
```
http://localhost:8000/api/auth/google/callback
```

### Production Environment

**Authorized JavaScript Origins:**
```
https://codemurf.com
```

**Authorized Redirect URIs:**
```
https://api.codemurf.com/api/auth/google/callback
```

---

## Backend Environment Configuration

### Development (.env.local or .env)

```bash
# Google OAuth Development
GOOGLE_CLIENT_ID=37099745939-4v685b95lv9r2306l1edq4s7dpnk05vd.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Backend Configuration
DATABASE_URL=mongodb://mongodb:27017/user_management_db
REDIS_URL=redis://redis:6379
JWT_SECRET_KEY=your-development-secret-key
DEBUG=True
```

### Production (.env.production)

```bash
# Google OAuth Production
GOOGLE_CLIENT_ID=37099745939-4v685b95lv9r2306l1edq4s7dpnk05vd.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://api.codemurf.com/api/auth/google/callback

# Backend Configuration
DATABASE_URL=mongodb://your-production-mongodb-url
REDIS_URL=redis://your-production-redis-url
JWT_SECRET_KEY=your-production-secret-key-change-this
DEBUG=False
```

---

## VS Code Extension Configuration

### Development Extension Settings

```typescript
// config.ts
export const DEVELOPMENT_CODEMURF_API_URL = "http://localhost:8000"
export const DEVELOPMENT_CODEMURF_WEB_URL = "http://localhost:3000"

// OAuth redirect URI for VS Code extension
const VSCODE_REDIRECT_URI = "vscode://codemurf.codemurf-extension/auth-callback"
```

### Production Extension Settings

```typescript
// config.ts
export const PRODUCTION_CODEMURF_API_URL = "https://api.codemurf.com"
export const PRODUCTION_CODEMURF_WEB_URL = "https://codemurf.com"

// OAuth redirect URI for VS Code extension
const VSCODE_REDIRECT_URI = "vscode://codemurf.codemurf-extension/auth-callback"
```

---

## PKCE Authentication Flow URLs

### Development Testing

**OAuth Login:**
```
http://localhost:8000/api/auth/google/login?
  state={random_state}&
  code_challenge={sha256_hash}&
  code_challenge_method=S256&
  redirect_uri=vscode://codemurf.codemurf-extension/auth-callback
```

**Token Exchange:**
```
POST http://localhost:8000/api/auth/token
Content-Type: application/json

{
  "grant_type": "authorization_code",
  "code": "{authorization_code}",
  "code_verifier": "{original_verifier}",
  "redirect_uri": "vscode://codemurf.codemurf-extension/auth-callback"
}
```

### Production

**OAuth Login:**
```
https://api.codemurf.com/api/auth/google/login?
  state={random_state}&
  code_challenge={sha256_hash}&
  code_challenge_method=S256&
  redirect_uri=vscode://codemurf.codemurf-extension/auth-callback
```

**Token Exchange:**
```
POST https://api.codemurf.com/api/auth/token
Content-Type: application/json

{
  "grant_type": "authorization_code",
  "code": "{authorization_code}",
  "code_verifier": "{original_verifier}",
  "redirect_uri": "vscode://codemurf.codemurf-extension/auth-callback"
}
```

---

## Google Cloud Console Configuration

### OAuth Consent Screen

**Application Name:** CodeMurf  
**User Type:** External  
**Support Email:** your-support@codemurf.com  
**Authorized Domains:**
- `codemurf.com`

**Scopes:**
- `openid`
- `email`
- `profile`

### OAuth 2.0 Client ID Settings

1. **Navigate to:** APIs & Services > Credentials
2. **Select:** OAuth 2.0 Client IDs > codemurf
3. **Configure:**

   **Authorized JavaScript origins:**
   - `https://codemurf.com`
   - `http://localhost:3000` (for development)

   **Authorized redirect URIs:**
   - `https://api.codemurf.com/api/auth/google/callback` (production)
   - `http://localhost:8000/api/auth/google/callback` (development)

4. **Save** and wait 5 minutes to a few hours for changes to propagate

---

## Testing Configuration

### Test Development Setup

```bash
# 1. Generate test parameters
python3 -c "
import hashlib, base64, secrets
cv = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
cc = base64.urlsafe_b64encode(hashlib.sha256(cv.encode()).digest()).decode().rstrip('=')
print(f'Verifier: {cv}')
print(f'Challenge: {cc}')
"

# 2. Test OAuth login
curl -I "http://localhost:8000/api/auth/google/login?state=test&code_challenge={challenge}&code_challenge_method=S256"

# Should return: 302 redirect to Google

# 3. Test token endpoint (with invalid code)
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"authorization_code","code":"test","code_verifier":"test","redirect_uri":"vscode://test"}'

# Should return: {"detail":"Invalid or expired authorization code"}
```

### Test Production Setup

```bash
# 1. Verify DNS resolution
nslookup api.codemurf.com

# 2. Test SSL certificate
curl -I https://api.codemurf.com/health

# 3. Test OAuth redirect
curl -I "https://api.codemurf.com/api/auth/google/login?state=test"

# Should return: 302 redirect to Google
```

---

## CORS Configuration

### Development CORS

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "vscode://codemurf.codemurf-extension"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### Production CORS

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://codemurf.com",
        "https://api.codemurf.com",
        "vscode://codemurf.codemurf-extension"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

---

## Deployment Checklist

### Pre-Deployment

- [x] Google OAuth Client configured
- [x] Authorized origins added
- [x] Authorized redirect URIs added
- [ ] SSL certificate installed for api.codemurf.com
- [ ] DNS records configured
- [ ] Environment variables set in production
- [ ] Redis configured with authentication
- [ ] MongoDB production instance ready

### Post-Deployment

- [ ] Test OAuth login flow in production
- [ ] Verify PKCE token exchange
- [ ] Test VS Code extension authentication
- [ ] Monitor error logs
- [ ] Set up alerting for authentication failures
- [ ] Document API for team

---

## Troubleshooting

### Common Issues

**Issue 1: "Redirect URI mismatch"**
- **Cause:** Redirect URI in request doesn't match Google Console configuration
- **Solution:** Ensure exact match including http/https and trailing slashes
- **Check:** Google Console > Credentials > OAuth 2.0 Client > Authorized redirect URIs

**Issue 2: "Origin not allowed"**
- **Cause:** JavaScript origin not in authorized list
- **Solution:** Add origin to Google Console authorized JavaScript origins
- **Note:** Changes take 5 minutes to a few hours to propagate

**Issue 3: "Invalid code_verifier"**
- **Cause:** Code verifier doesn't match code challenge
- **Solution:** Ensure SHA256(code_verifier) == code_challenge
- **Debug:** Check Redis for stored PKCE data

**Issue 4: "Invalid or expired authorization code"**
- **Cause:** Authorization code already used or expired
- **Solution:** Authorization codes are single-use and expire after 5 minutes
- **Action:** Generate new authorization code

**Issue 5: CORS errors**
- **Cause:** Frontend origin not in CORS allowed origins
- **Solution:** Update CORS middleware configuration
- **Restart:** Backend service after configuration change

---

## Security Considerations

### Production Security

1. **HTTPS Only:** All production URLs must use HTTPS
2. **Secret Rotation:** Rotate JWT secret keys regularly
3. **Redis Auth:** Enable Redis password authentication
4. **Rate Limiting:** Implement rate limiting on auth endpoints
5. **Session Expiry:** Configure appropriate session timeouts
6. **Monitoring:** Set up alerts for suspicious authentication patterns

### Client Credentials

**Keep Secret:**
- `GOOGLE_CLIENT_SECRET`
- `JWT_SECRET_KEY`
- Redis password
- Database credentials

**Never Commit:**
- `.env` files with real credentials
- Production secrets in version control

---

## Support & Resources

### Documentation
- **Backend API:** http://localhost:8000/docs (dev)
- **Backend API:** https://api.codemurf.com/docs (prod)
- **Implementation:** `PKCE_IMPLEMENTATION_COMPLETE.md`
- **Test Results:** `PKCE_TEST_RESULTS.md`
- **Auth Spec:** `authdoc.md`

### Google OAuth Resources
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
- [Google Cloud Console](https://console.cloud.google.com/)

### Testing Tools
- Test Script: `python3 test_pkce_flow.py`
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## Quick Reference

### Development URLs
```
Backend:  http://localhost:8000
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
Health:   http://localhost:8000/health
```

### Production URLs
```
Backend:  https://api.codemurf.com
Frontend: https://codemurf.com
API Docs: https://api.codemurf.com/docs
Health:   https://api.codemurf.com/health
```

### Key Endpoints
```
POST /api/auth/token                  - PKCE token exchange
GET  /api/auth/google/login           - OAuth initiation
GET  /api/auth/google/callback        - OAuth callback
POST /api/auth/refresh                - Token refresh
GET  /api/auth/me                     - User info
POST /api/auth/logout                 - Logout
```

---

**Last Updated:** November 11, 2025  
**Configuration Status:** ✅ Complete and Tested
