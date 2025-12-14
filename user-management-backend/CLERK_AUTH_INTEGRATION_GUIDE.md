# 🔐 Clerk Authentication Integration Guide

## Overview

This guide explains how to properly integrate Clerk authentication between your Next.js frontend and FastAPI backend running in Docker.

## 🏗️ Architecture

```
Frontend (Next.js + Clerk)
    ↓ User signs in with Clerk
    ↓ Gets JWT session token
    ↓
    ↓ API Request: Authorization: Bearer <clerk_jwt>
    ↓
Backend (FastAPI in Docker)
    ↓ Validates JWT with Clerk JWKS
    ↓ Creates/updates user in MongoDB
    ↓ Returns user data/API response
```

## ✅ What Was Fixed

### 1. **Proper JWT Verification**
- ✅ Implemented JWKS-based token verification
- ✅ Added fallback to unverified tokens in debug mode
- ✅ Proper error handling and logging
- ✅ Support for token signature validation

### 2. **Docker Configuration**
- ✅ Added Clerk environment variables to docker-compose.yml
- ✅ Updated .env file with Clerk credentials
- ✅ Proper environment variable propagation to containers

### 3. **CORS Configuration**
- ✅ Added explicit header allowlist
- ✅ Added localhost IPv4 variants
- ✅ Increased preflight cache time
- ✅ Added PATCH method support

### 4. **Enhanced Logging**
- ✅ Better error messages with emojis
- ✅ Detailed token verification logging
- ✅ Helpful debugging output

## 🚀 Setup Instructions

### Step 1: Backend Configuration

1. **Update Environment Variables** (already done)
   ```bash
   cd user-management-backend
   # Check that .env has these values:
   cat .env | grep CLERK
   ```

2. **Rebuild Docker Containers**
   ```bash
   # Stop existing containers
   docker-compose down
   
   # Rebuild with new configuration
   docker-compose build --no-cache
   
   # Start containers
   docker-compose up -d
   
   # Check logs
   docker-compose logs -f api
   ```

3. **Verify Backend is Running**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"ok"}
   ```

### Step 2: Frontend Configuration

1. **Check Clerk Environment Variables**
   
   Navigate to your frontend directory and verify `.env.local`:
   ```bash
   cd C:\Users\Asus\Desktop\Autogenlabs-Web-App
   ```
   
   Ensure these variables exist:
   ```env
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2JA
   CLERK_SECRET_KEY=sk_test_FtxbYvBnDrtJ7ajXTT0N8ehm3iQxNK1DYaCOY1jEhu
   NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
   NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
   NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
   NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
   
   # Backend API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. **Update API Client to Send Clerk Token**

   In your frontend API client (likely in `src/lib/api.ts` or similar):
   ```typescript
   import { useAuth } from '@clerk/nextjs';
   
   // In your API call function
   const { getToken } = useAuth();
   
   const makeApiRequest = async (endpoint: string, options = {}) => {
     // Get Clerk session token
     const token = await getToken();
     
     const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
       ...options,
       headers: {
         'Authorization': `Bearer ${token}`,
         'Content-Type': 'application/json',
         ...options.headers,
       },
     });
     
     return response;
   };
   ```

### Step 3: Test the Integration

1. **Run Diagnostic Script**
   ```bash
   cd user-management-backend
   python test_clerk_auth_flow.py
   ```
   
   This will check:
   - ✅ Backend health
   - ✅ Clerk JWKS endpoint accessibility
   - ✅ CORS configuration
   - ✅ Public endpoints
   - ✅ Registration flow

2. **Test with Real User**
   
   a. Start your frontend:
   ```bash
   cd C:\Users\Asus\Desktop\Autogenlabs-Web-App
   npm run dev
   ```
   
   b. Open http://localhost:3000
   
   c. Sign in with Clerk
   
   d. Open DevTools > Network tab
   
   e. Make an API request (e.g., to `/api/auth/me`)
   
   f. Verify the request has `Authorization: Bearer <token>` header
   
   g. Check the response is 200 OK with user data

3. **Check Backend Logs**
   ```bash
   docker-compose logs -f api
   ```
   
   Look for:
   - ✅ "Clerk token verified for user: user_xxx"
   - ✅ "Authenticated via Authorization header (Clerk JWT)"
   - ❌ Any error messages

## 🔍 Common Issues & Solutions

### Issue 1: 401 Unauthorized Error

**Symptoms:**
- Frontend gets 401 when calling backend API
- Backend logs show "Could not validate credentials"

**Solutions:**
1. Check that Clerk token is being sent:
   ```javascript
   // In browser DevTools Console
   const { getToken } = useAuth();
   const token = await getToken();
   console.log('Token:', token);
   ```

2. Verify backend has correct Clerk credentials:
   ```bash
   docker-compose exec api env | grep CLERK
   ```

3. Check token in JWT debugger (https://jwt.io):
   - Paste your token
   - Verify `iss` claim matches: `https://apt-clam-53.clerk.accounts.dev`
   - Check token hasn't expired (`exp` claim)

### Issue 2: CORS Error

**Symptoms:**
- Browser console shows CORS error
- Preflight request fails

**Solutions:**
1. Verify frontend origin is in allowed list:
   ```python
   # In app/main.py, check allow_origins includes:
   "http://localhost:3000"
   ```

2. Check that credentials are included in fetch:
   ```javascript
   fetch(url, {
     credentials: 'include',  // Important!
     headers: { 'Authorization': `Bearer ${token}` }
   })
   ```

3. Restart backend after CORS changes:
   ```bash
   docker-compose restart api
   ```

### Issue 3: User Not Created in Database

**Symptoms:**
- Authentication succeeds but user data missing
- Backend logs show "Created new user from Clerk"

**Solutions:**
1. Check MongoDB connection:
   ```bash
   docker-compose exec mongodb mongosh user_management_db --eval "db.users.find().pretty()"
   ```

2. Verify Beanie initialization:
   ```bash
   docker-compose logs api | grep "Database connected"
   ```

3. Check user model has clerk_id field:
   ```bash
   docker-compose exec mongodb mongosh user_management_db --eval "db.users.findOne()"
   ```

### Issue 4: Token Verification Fails

**Symptoms:**
- Backend logs show "JWKS verification failed"
- Falls back to unverified token

**Solutions:**
1. Check Clerk JWKS endpoint is accessible:
   ```bash
   curl https://apt-clam-53.clerk.accounts.dev/.well-known/jwks.json
   ```

2. Verify backend can make HTTPS requests:
   ```bash
   docker-compose exec api python -c "import httpx; print(httpx.get('https://www.google.com').status_code)"
   ```

3. Check if using correct Clerk instance:
   - Go to Clerk Dashboard > API Keys
   - Verify Frontend API matches: `apt-clam-53.clerk.accounts.dev`

## 📊 Testing Checklist

- [ ] Backend starts without errors
- [ ] Clerk JWKS endpoint is accessible
- [ ] CORS headers are correct
- [ ] Health check returns 200 OK
- [ ] Registration endpoint works
- [ ] Frontend can sign in with Clerk
- [ ] API requests include Authorization header
- [ ] Backend validates Clerk token
- [ ] User is created/updated in MongoDB
- [ ] User data is returned in API response
- [ ] Subsequent requests work with same token
- [ ] Token expiration is handled correctly

## 🔐 Security Considerations

### Development (Current)
- ✅ JWKS verification implemented
- ✅ Falls back to unverified in debug mode
- ✅ Proper token validation
- ⚠️ Using test Clerk keys

### Production (Before Deployment)
1. **Use Production Clerk Keys**
   ```env
   CLERK_SECRET_KEY=sk_live_...
   CLERK_PUBLISHABLE_KEY=pk_live_...
   ```

2. **Disable Debug Mode**
   ```env
   DEBUG=False
   ```

3. **Update CORS Origins**
   ```python
   allow_origins=["https://your-production-domain.com"]
   ```

4. **Enable HTTPS Only**
   ```python
   # In production, reject non-HTTPS requests
   ```

5. **Set Secure Cookies**
   ```python
   # Clerk handles this, but verify in production
   ```

## 📞 Support & Debugging

### Useful Commands

```bash
# Check container status
docker-compose ps

# View backend logs
docker-compose logs -f api

# View MongoDB logs
docker-compose logs -f mongodb

# Restart specific service
docker-compose restart api

# Rebuild and restart
docker-compose up -d --build api

# Access MongoDB shell
docker-compose exec mongodb mongosh user_management_db

# Check environment variables
docker-compose exec api env | grep CLERK

# Test health endpoint
curl http://localhost:8000/health

# Test with auth token
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/auth/me
```

### Log Interpretation

**Good Logs:**
```
✅ Database connected and initialized
✅ Using Clerk authentication
✅ Clerk token verified for user: user_2xxx
✅ Authenticated via Authorization header (Clerk JWT)
```

**Warning Logs:**
```
⚠️ JWKS verification failed: <reason>
⚠️ Using unverified token in debug mode
```

**Error Logs:**
```
❌ Token missing 'sub' claim
❌ Invalid issuer: <issuer>
❌ No matching key found in JWKS for kid: <kid>
❌ JWT verification error: <error>
```

## 🎯 Next Steps

1. **Test the complete flow:**
   - Run diagnostic script
   - Sign in on frontend
   - Make API calls
   - Verify in backend logs

2. **Monitor and optimize:**
   - Check response times
   - Monitor error rates
   - Optimize database queries

3. **Prepare for production:**
   - Update to production Clerk keys
   - Configure production CORS
   - Enable proper logging
   - Set up monitoring

## 📚 References

- [Clerk Authentication Docs](https://clerk.com/docs)
- [Manual JWT Verification](https://clerk.com/docs/guides/sessions/manual-jwt-verification)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

**Last Updated:** November 16, 2025  
**Status:** ✅ Ready for testing
