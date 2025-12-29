# 🚀 Quick Start - Clerk Authentication Fix

**Last Updated:** November 16, 2025

## ⚡ TL;DR - Get Running in 3 Steps

```bash
# 1. Restart Docker with new config
.\restart_with_clerk.ps1

# 2. Test everything works
python test_clerk_auth_flow.py

# 3. Check logs
docker-compose logs -f api
```

Done! ✅

---

## 📝 What Was Fixed?

✅ **Proper JWT verification** - Now uses Clerk's JWKS for secure token validation  
✅ **Docker configuration** - Clerk environment variables added  
✅ **Better CORS** - Explicit headers and better security  
✅ **Testing tools** - Diagnostic script to verify everything works  
✅ **Documentation** - Complete guides for setup and troubleshooting  

---

## 🔧 Detailed Steps

### Step 1: Restart Backend

**Windows (PowerShell):**
```powershell
cd user-management-backend
.\restart_with_clerk.ps1
```

**Linux/Mac:**
```bash
cd user-management-backend
chmod +x restart_with_clerk.sh
./restart_with_clerk.sh
```

This will:
- Stop existing containers
- Rebuild with Clerk configuration
- Start everything up
- Verify it's working

**Expected output:**
```
✅ Containers are running
✅ Backend is healthy
```

### Step 2: Run Tests

```bash
python test_clerk_auth_flow.py
```

**Expected results:**
- ✅ Health Check: PASSED
- ✅ JWKS Endpoint: PASSED
- ✅ CORS Configuration: PASSED
- ✅ Public Endpoints: PASSED
- ✅ Registration: PASSED
- ✅ Environment Check: PASSED
- ⚠️  Clerk Token Auth: SKIPPED (needs real token)

### Step 3: Configure Frontend

1. **Check environment variables** in `C:\Users\Asus\Desktop\Autogenlabs-Web-App\.env.local`:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2JA
CLERK_SECRET_KEY=sk_test_FtxbYvBnDrtJ7ajXTT0N8ehm3iQxNK1DYaCOY1jEhu
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. **Update API client** to send Clerk token:

```typescript
// In your API utility file (e.g., src/lib/api.ts)
import { useAuth } from '@clerk/nextjs';

const { getToken } = useAuth();
const token = await getToken();

fetch(`${API_URL}/api/endpoint`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
})
```

3. **Start frontend:**

```bash
cd C:\Users\Asus\Desktop\Autogenlabs-Web-App
npm run dev
```

### Step 4: Test End-to-End

1. Open http://localhost:3000
2. Sign in with Clerk
3. Open DevTools > Network tab
4. Make an API request
5. Check request has `Authorization: Bearer <token>` header
6. Verify response is 200 OK

**Backend logs should show:**
```
✅ Clerk token verified for user: user_xxx
✅ Authenticated via Authorization header (Clerk JWT)
```

---

## 🔍 Verify Everything Works

### Quick Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

### Check Docker Status

```bash
docker-compose ps
```

Expected: All services "Up"

### View Logs

```bash
docker-compose logs -f api
```

Look for:
- ✅ "Database connected and initialized"
- ✅ "Using Clerk authentication"

### Check Environment

```bash
docker-compose exec api env | grep CLERK
```

Expected output should show all 4 Clerk variables.

---

## ❓ Common Issues

### Issue: "Cannot connect to backend"

**Solution:**
```bash
docker-compose restart api
docker-compose logs api
```

### Issue: "401 Unauthorized"

**Check:**
1. Is Clerk token being sent from frontend?
2. Are Clerk env vars set correctly?
3. Is token expired?

**Debug:**
```bash
# Check logs for specific error
docker-compose logs api | grep -i error

# Verify environment
docker-compose exec api env | grep CLERK
```

### Issue: "CORS Error"

**Solution:**
```bash
# Restart backend
docker-compose restart api

# Verify frontend origin is in allowed list
# Should be http://localhost:3000
```

### Issue: "User not created"

**Check:**
```bash
# Verify MongoDB is running
docker-compose ps mongodb

# Check database connection
docker-compose logs api | grep "Database"

# Access MongoDB
docker-compose exec mongodb mongosh user_management_db --eval "db.users.find().pretty()"
```

---

## 📚 More Help

- **Complete Setup Guide:** `CLERK_AUTH_INTEGRATION_GUIDE.md`
- **What Changed:** `CLERK_AUTH_FIX_SUMMARY.md`
- **Original Migration:** `CLERK_INTEGRATION_SUMMARY.md`

---

## ✅ Success Checklist

- [ ] Docker containers are running
- [ ] Backend health check passes
- [ ] Diagnostic script shows mostly PASSED
- [ ] Frontend has Clerk env vars
- [ ] Can sign in with Clerk on frontend
- [ ] API requests include Authorization header
- [ ] Backend logs show "Clerk token verified"
- [ ] User data is returned from API

**All checked?** You're good to go! 🎉

---

## 🆘 Still Having Issues?

1. **Check logs:**
   ```bash
   docker-compose logs -f api
   ```

2. **Run full diagnostic:**
   ```bash
   python test_clerk_auth_flow.py
   ```

3. **Verify configuration:**
   - Backend: Check `docker-compose.yml` has Clerk vars
   - Frontend: Check `.env.local` has Clerk keys
   - Both: Keys should match (same Clerk instance)

4. **Read the guide:**
   ```bash
   # Open the complete guide
   code CLERK_AUTH_INTEGRATION_GUIDE.md
   ```

5. **Check Clerk Dashboard:**
   - Go to https://dashboard.clerk.com
   - API Keys section
   - Verify keys match your configuration

---

**Need more details?** See `CLERK_AUTH_INTEGRATION_GUIDE.md` for comprehensive troubleshooting and setup instructions.
