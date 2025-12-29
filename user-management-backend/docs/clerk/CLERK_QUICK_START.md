# 🚀 CLERK AUTHENTICATION - QUICK START

## ⚡ Start Backend with Clerk

### 1. Add Environment Variables
Create/update `.env` file:
```bash
CLERK_SECRET_KEY=sk_test_FtxbYvBnDrtJ7ajXTT0N8ehm3iQxNK1DYaCOY1jEhu
CLERK_PUBLISHABLE_KEY=pk_test_YXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2JA
CLERK_FRONTEND_API=apt-clam-53.clerk.accounts.dev
CLERK_JWKS_URL=https://apt-clam-53.clerk.accounts.dev/.well-known/jwks.json
```

### 2. Start Server
```bash
cd user-management-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Check Logs
You should see:
```
✅ Using Clerk authentication - OAuth registration skipped
✅ Database connected and initialized
```

## 🎯 Authentication Methods Supported

| Method | Header | Use Case | Status |
|--------|--------|----------|--------|
| Clerk JWT | `Authorization: Bearer <clerk_jwt>` | Frontend web app | ✅ NEW |
| API Key (X-Header) | `X-API-Key: sk_xxx` | VS Code extension | ✅ Works |
| API Key (Bearer) | `Authorization: Bearer sk_xxx` | Extension fallback | ✅ Works |
| Legacy JWT | `Authorization: Bearer <jwt>` | Old systems | ✅ Works |

## 📝 Code Examples

### Protect Any Route
```python
from app.auth.unified_auth import get_current_user_unified
from app.models.user import User
from fastapi import Depends

@router.get("/api/protected")
async def protected(current_user: User = Depends(get_current_user_unified)):
    return {"user": current_user.email}
```

### Optional Auth
```python
from app.auth.unified_auth import get_optional_current_user_unified

@router.get("/api/public")
async def public(current_user: Optional[User] = Depends(get_optional_current_user_unified)):
    if current_user:
        return {"auth": True, "user": current_user.email}
    return {"auth": False}
```

## 🧪 Quick Test

### Test Clerk Auth
```bash
# Get Clerk token from frontend
# Then test API:
curl -H "Authorization: Bearer <clerk_jwt>" http://localhost:8000/api/me
```

### Test API Key (Extension)
```bash
curl -H "X-API-Key: sk_your_key" http://localhost:8000/api/me
```

## 🔍 Debug Checklist

- [ ] `.env` has `CLERK_SECRET_KEY`
- [ ] Backend starts without errors
- [ ] Logs show "Using Clerk authentication"
- [ ] Frontend can get Clerk token
- [ ] API calls include `Authorization` header
- [ ] Backend logs show "Clerk token verified"
- [ ] Users are created in MongoDB

## 📊 What Changed

### ✅ Added
- `app/auth/clerk_auth.py` - Clerk verification
- `app/models/user.py` - `clerk_id`, `first_name`, `last_name` fields
- `.env.example` - Clerk variables

### 🔄 Updated
- `app/auth/unified_auth.py` - Supports Clerk JWT
- `app/main.py` - Commented old OAuth
- `app/config.py` - Clerk settings

### ❌ Removed
- Nothing! Full backward compatibility

## 🎊 Success = 

✅ Backend starts
✅ No errors in logs
✅ "Using Clerk authentication" message
✅ Frontend sign-in works
✅ API calls succeed with Clerk token
✅ Extension still works with API keys

---

**Need more details?** Check `CLERK_INTEGRATION_SUMMARY.md`
