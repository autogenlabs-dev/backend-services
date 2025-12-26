# Quick Clerk Authentication Test Guide

## Running the Test

### Option 1: Run Python Test Script Directly
```bash
cd user-management-backend
python test_clerk_e2e_flow.py
```

### Option 2: Run Batch Script (Windows)
```bash
test_auth_flow.bat
```

## What the Test Checks

1. **Backend Health** - Verifies backend is running on port 8000
2. **CORS Configuration** - Checks CORS headers are properly set
3. **Unprotected Endpoints** - Tests public endpoints work
4. **Protected Endpoints** - Verifies auth is required
5. **Token Verification** - Tests Clerk JWT validation
6. **API Key Endpoint** - Checks API key management
7. **Database Connection** - Validates DB configuration
8. **Token Exchange** - Tests Clerk token exchange flow

## Manual Testing with Real Clerk Token

1. **Start Backend:**
   ```bash
   cd user-management-backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Get Clerk Token from Frontend:**
   - Sign in to your app via Clerk
   - Open browser console
   - Run: `await window.Clerk.session.getToken()`
   - Copy the token

3. **Test Backend with Token:**
   ```bash
   curl -H "Authorization: Bearer YOUR_CLERK_TOKEN" http://localhost:8000/api/auth/me
   ```

4. **Test API Key Retrieval:**
   ```bash
   curl -H "Authorization: Bearer YOUR_CLERK_TOKEN" http://localhost:8000/api/user/api-key
   ```

## Expected Response from /api/auth/me

```json
{
  "id": "user_id_here",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "last_login_at": "2024-01-01T00:00:00"
}
```

## Expected Response from /api/user/api-key

```json
{
  "api_key": "your_api_key_here",
  "created_at": "2024-01-01T00:00:00"
}
```

## Common Issues and Solutions

### Issue: Backend Not Running
**Error:** `Cannot connect to backend at http://localhost:8000`
**Solution:** Start the backend server first

### Issue: 401 Unauthorized
**Error:** `Could not validate credentials`
**Solutions:**
- Check if Clerk token is valid (not expired)
- Verify CLERK_SECRET_KEY is set in .env
- Ensure token is sent in Authorization header: `Bearer <token>`

### Issue: CORS Error
**Error:** `Access to fetch has been blocked by CORS policy`
**Solution:** Check that frontend origin is in CORS allowed_origins in main.py

### Issue: Database Connection Error
**Error:** `Could not connect to database`
**Solution:** 
- Check MongoDB is running
- Verify DATABASE_URL in .env file
- Ensure MongoDB connection string is correct

## Frontend Integration Checklist

- [ ] Clerk SDK installed (`@clerk/clerk-react`)
- [ ] ClerkProvider wraps app with correct publishableKey
- [ ] Using `getToken()` from `useAuth()` hook
- [ ] Token sent in Authorization header as `Bearer <token>`
- [ ] Backend URL configured correctly (http://localhost:8000 for dev)
- [ ] Error handling for 401 responses

## Testing Workflow

1. Start backend server
2. Run this test script to verify backend setup
3. Start frontend application
4. Sign in via Clerk
5. Check browser network tab for API calls
6. Verify Authorization header is present
7. Check API responses in network tab

## Debugging Tips

- Enable debug mode in backend: `DEBUG=True` in .env
- Check backend logs for authentication errors
- Use browser DevTools Network tab to inspect requests
- Use Clerk Dashboard to view user sessions and tokens
- Check MongoDB to verify users are being created/synced

## Contact

If tests fail, check:
- Backend logs
- Frontend console logs
- MongoDB connection
- Clerk dashboard for token issues
