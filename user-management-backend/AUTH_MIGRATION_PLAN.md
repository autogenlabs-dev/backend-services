# Authentication & API Key Management Implementation Plan

## Current State Analysis

### Backend (Python/FastAPI)
- **Database**: MongoDB with Beanie ODM
- **Auth Methods**: 
  - JWT-based auth (email/password)
  - Google OAuth
  - Extension auth (ticket-based for VS Code)
- **Models**: User, ApiKey, UserSubscription, SubscriptionPlan
- **Existing Features**:
  - User registration/login
  - API key generation and management
  - Subscription plans (free, pro, enterprise)
  - Token-based rate limiting
  - Extension authentication flow

### Frontend (Next.js 15)
- **Current Auth**: Clerk (client-side only)
- **Issue**: Clerk is not connected to backend database
- **Components**:
  - ClerkProviderWrapper
  - AutoProvisionUser (calls backend provision endpoint)
  - SignInSuccessHandler (generates JWT for extension)

### VS Code Extension
- **Expected Flow**: 
  - User signs in → receives API key
  - API key auto-saved in extension settings
  - Extension uses API key for backend calls

---

## 🎯 Goal: Unified Auth Flow

### User Journey
1. User signs up/logs in on **web app** (frontend)
2. Backend **creates user account** in MongoDB
3. Backend **generates personal API key** for the user
4. When user connects **VS Code extension**:
   - Extension redirects to web for login
   - After login, extension receives API key automatically
   - API key is saved in extension settings
5. Extension uses API key for all backend calls
6. Backend validates API key and applies user's subscription limits

---

## 📋 Implementation Plan

### Phase 1: Remove Clerk from Backend Connection

#### What to Keep
- ✅ Clerk on frontend for UI/UX (sign-in components)
- ✅ Clerk session management on client side

#### What to Remove/Replace
- ❌ Remove `ClerkProviderWrapper` dependency on backend
- ❌ Remove `/api/auth/provision-user` route from frontend
- ❌ Remove Clerk secret key from backend

#### What to Add
- ✅ Frontend calls backend `/api/auth/register` or `/api/auth/login`
- ✅ Backend returns JWT + API key
- ✅ Frontend stores JWT for authenticated requests

### Phase 2: Backend Implementation (Already ~80% Complete!)

#### Existing Endpoints (Working)
```
✅ POST /api/auth/register - Create user account
✅ POST /api/auth/login - Login with email/password
✅ POST /api/auth/google/login - Google OAuth
✅ GET /api/auth/google/callback - OAuth callback
✅ GET /api/auth/me - Get current user
✅ POST /api/keys - Create API key
✅ GET /api/keys - List user's API keys
✅ DELETE /api/keys/{key_id} - Revoke API key
```

#### What Needs to be Added/Modified

**1. Auto-Generate API Key on User Creation**
```python
# File: app/services/user_service.py
# Modify create_user_with_password() to:
async def create_user_with_password(db, user_data):
    # ... existing user creation ...
    
    # Auto-generate API key for new user
    api_key = await auto_generate_user_api_key(db, user.id)
    
    return user, api_key
```

**2. New Endpoint: Get User's Active API Key**
```python
# File: app/api/users.py
@router.get("/me/api-key")
async def get_my_api_key(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's primary API key for extension usage"""
    api_key = await ApiKey.find_one(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    ).sort(-ApiKey.created_at)
    
    if not api_key:
        # Auto-generate if none exists
        api_key = await auto_generate_user_api_key(db, current_user.id)
    
    return {
        "api_key": api_key.key_preview,  # Only return preview for security
        "full_key": api_key.full_key,    # Only on first creation
        "name": api_key.name,
        "created_at": api_key.created_at
    }
```

**3. Modified Extension Auth Flow**
```python
# File: app/api/extension_auth.py
# Update /v1/client/sign_ins to return API key:

@router.post("/v1/client/sign_ins")
async def client_sign_ins(...):
    # ... existing ticket validation ...
    
    # Get or create user's API key
    api_key = await get_or_create_user_api_key(db, user.id)
    
    response = JSONResponse(
        content={
            "response": {
                "created_session_id": session_id,
                "api_key": api_key.full_key,  # Send full key to extension
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "subscription": user.subscription,
                    "tokens_remaining": user.tokens_remaining
                }
            }
        }
    )
    response.headers["Authorization"] = f"Bearer {client_token}"
    
    return response
```

### Phase 3: Frontend Implementation

#### Remove Clerk Backend Dependencies

**1. Update `src/app/layout.js`**
```javascript
// Keep ClerkProvider for UI
// Remove AutoProvisionUser component (not needed)
import ClerkProviderWrapper from "../components/auth/ClerkProviderWrapper";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ClerkProviderWrapper>
          {/* Remove AutoProvisionUser */}
          <LayoutWrapper>{children}</LayoutWrapper>
        </ClerkProviderWrapper>
      </body>
    </html>
  );
}
```

**2. Create New Auth Context** (Replace Clerk backend calls)
```typescript
// File: src/contexts/BackendAuthContext.tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '@clerk/nextjs';

const BackendAuthContext = createContext(null);

export function BackendAuthProvider({ children }) {
  const { user, isLoaded } = useUser();  // Clerk user for UI
  const [backendUser, setBackendUser] = useState(null);
  const [apiKey, setApiKey] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoaded || !user) {
      setLoading(false);
      return;
    }

    // Call backend to get/create user and API key
    async function syncBackendAuth() {
      try {
        // Option 1: If user exists in backend
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('backend_token')}`
          }
        });

        if (res.ok) {
          const data = await res.json();
          setBackendUser(data);
          
          // Get API key
          const keyRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/me/api-key`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('backend_token')}`
            }
          });
          
          if (keyRes.ok) {
            const keyData = await keyRes.json();
            setApiKey(keyData.full_key || keyData.api_key);
          }
        } else {
          // Option 2: Create backend user from Clerk data
          const registerRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: user.emailAddresses[0].emailAddress,
              password: null, // OAuth user
              name: user.fullName || user.firstName,
              clerk_id: user.id
            })
          });

          if (registerRes.ok) {
            const data = await registerRes.json();
            localStorage.setItem('backend_token', data.access_token);
            setBackendUser(data.user);
            setApiKey(data.api_key);
          }
        }
      } catch (error) {
        console.error('Backend auth sync failed:', error);
      } finally {
        setLoading(false);
      }
    }

    syncBackendAuth();
  }, [user, isLoaded]);

  return (
    <BackendAuthContext.Provider value={{ backendUser, apiKey, loading }}>
      {children}
    </BackendAuthContext.Provider>
  );
}

export const useBackendAuth = () => useContext(BackendAuthContext);
```

**3. Update Extension Auth Handler**
```typescript
// File: src/components/auth/SignInSuccessHandler.tsx
// Modify to pass backend API key to extension

export function SignInSuccessHandler() {
  const { apiKey } = useBackendAuth();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!isSignedIn || source !== 'vscode' || !apiKey) return;

    async function sendToExtension() {
      // Generate deep link with API key
      const deepLink = `vscode://codemurf.codemurf/auth?apiKey=${apiKey}&email=${user.email}`;
      window.location.href = deepLink;
    }

    sendToExtension();
  }, [isSignedIn, apiKey]);
  
  // ... rest of component
}
```

### Phase 4: VS Code Extension Integration

#### Extension Receives API Key
```typescript
// Extension auth handler
vscode.window.registerUriHandler({
  handleUri(uri: vscode.Uri) {
    const apiKey = uri.query.get('apiKey');
    const email = uri.query.get('email');
    
    // Save API key to extension settings
    await vscode.workspace.getConfiguration('codemurf').update(
      'apiKey',
      apiKey,
      vscode.ConfigurationTarget.Global
    );
    
    vscode.window.showInformationMessage('✅ Successfully authenticated!');
  }
});
```

#### Extension Uses API Key
```typescript
// All API calls use the saved API key
const apiKey = vscode.workspace.getConfiguration('codemurf').get('apiKey');

const response = await fetch('http://localhost:8000/api/llm/completion', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ prompt: '...' })
});
```

---

## 🔐 Security Considerations

### API Key Management
1. **Generation**: Use `secrets.token_urlsafe(32)` for secure random keys
2. **Storage**: Store hashed version in database (bcrypt or SHA256)
3. **Transmission**: Only send full key once (on creation), then show preview
4. **Validation**: Fast lookup by hash, verify user subscription status
5. **Rotation**: Users can revoke and create new keys anytime

### Rate Limiting
```python
# Already implemented in backend
- Free tier: 60 requests/minute
- Pro tier: 300 requests/minute
- Enterprise: 1000 requests/minute
```

### Token Flow
```
Frontend (Clerk) ──JWT──> Backend
                          ↓
                    Validates JWT
                          ↓
                    Returns API Key
                          ↓
Extension <──API Key──── Backend
          ↓
    Stores in Settings
          ↓
    Uses for All Requests
```

---

## 📊 Database Schema (Already Exists!)

### User Model
```python
class User(Document):
    email: EmailStr
    password_hash: Optional[str]
    clerk_id: Optional[str]  # For Clerk integration
    subscription: str  # "free", "pro", "enterprise"
    tokens_remaining: int
    tokens_used: int
    is_active: bool
    role: UserRole
```

### ApiKey Model
```python
class ApiKey(Document):
    user_id: PydanticObjectId
    key_hash: str  # Hashed API key
    key_preview: str  # "sk_...abc123" (first 8 chars)
    name: str
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
```

### UserSubscription Model
```python
class UserSubscription(Document):
    user_id: PydanticObjectId
    plan_id: PydanticObjectId
    status: str  # "active", "inactive", "cancelled"
    current_period_end: datetime
```

---

## ✅ Implementation Checklist

### Backend Tasks
- [ ] Add `auto_generate_user_api_key()` function
- [ ] Modify `/api/auth/register` to return API key
- [ ] Modify `/api/auth/login` to return API key
- [ ] Add `/api/users/me/api-key` endpoint
- [ ] Update `/api/extension/sign_ins` to include API key
- [ ] Test API key validation middleware
- [ ] Test rate limiting per subscription tier

### Frontend Tasks
- [ ] Remove `AutoProvisionUser` component
- [ ] Remove `/api/auth/provision-user` route
- [ ] Create `BackendAuthContext`
- [ ] Update `SignInSuccessHandler` to pass API key
- [ ] Add API key display in user dashboard
- [ ] Add "Copy API Key" button in settings
- [ ] Test Clerk UI → Backend sync flow

### Extension Tasks
- [ ] Update auth handler to receive API key
- [ ] Store API key in extension settings
- [ ] Update all API calls to use API key
- [ ] Add "Sign Out" command (clears API key)
- [ ] Add settings UI to manually enter API key
- [ ] Test auto-login flow from web

### Testing
- [ ] User signs up → API key generated
- [ ] User logs in → API key retrieved
- [ ] Extension connects → API key saved
- [ ] Extension makes API call → backend validates
- [ ] Rate limiting works per tier
- [ ] User can revoke/regenerate API key
- [ ] Subscription upgrade → rate limits update

---

## 🚀 Deployment Steps

### 1. Backend Deployment
```bash
cd user-management-backend
# Update .env with production values
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Deployment
```bash
cd Autogenlabs-Web-App
# Set environment variables in Vercel:
# - NEXT_PUBLIC_API_URL=https://api.codemurf.com
# - Keep Clerk keys for frontend auth
npm run build
vercel deploy --prod
```

### 3. Extension Update
- Update extension to use new auth flow
- Publish new version to VS Code marketplace
- Users will need to re-authenticate

---

## 📈 Benefits of This Approach

### ✅ Pros
1. **Single Source of Truth**: Backend database controls everything
2. **Simple for Users**: One API key for all extension features
3. **Secure**: API keys can be rotated, Clerk handles frontend
4. **Scalable**: Easy to add subscription tiers and limits
5. **Maintainable**: Clerk for UI, backend for business logic
6. **Flexible**: Users can use API key directly or via extension

### 🎯 User Experience
- User signs up once
- API key automatically provisioned
- Extension auto-configures on first connect
- Seamless experience across web and extension

---

## 🔄 Migration Path

### For Existing Users
1. Deploy backend changes first
2. Existing users will auto-generate API key on next login
3. Frontend update removes Clerk backend dependency
4. Extension update adds API key storage
5. Users re-authenticate once to get API key
6. Old OAuth tokens still work during transition period

### Rollback Plan
- Keep old OAuth endpoints for 30 days
- Monitor error rates
- Gradual rollout via feature flags

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Implement backend changes** - ~2-3 hours
3. **Update frontend** - ~2-3 hours
4. **Test end-to-end** - ~1 hour
5. **Deploy to staging** - Test with real users
6. **Production deployment** - Coordinate timing
7. **Update documentation** - User guides and API docs

---

## Questions to Answer

1. ❓ Should API keys expire? (Recommendation: No expiration, but allow manual rotation)
2. ❓ Allow multiple API keys per user? (Recommendation: Yes, for different devices)
3. ❓ Show API key in dashboard? (Recommendation: Yes, with "reveal" button)
4. ❓ Email notification on API key creation? (Recommendation: Yes, security best practice)
5. ❓ 2FA for API key operations? (Recommendation: Later phase)

---

**Status**: Ready for implementation
**Estimated Time**: 6-8 hours total
**Risk Level**: Low (mostly additive changes)
**Breaking Changes**: Extension needs re-authentication (one-time)
