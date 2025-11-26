# Clerk JWT Token Configuration Guide

## Current Issue

JWT tokens are expiring too quickly (default: 60 seconds), causing test failures.

## Solution: Increase Token Lifetime

### Method 1: Clerk Dashboard (Recommended)

1. **Access Clerk Dashboard**

   - URL: https://dashboard.clerk.com
   - Login with your account
   - Select your application: "apt-clam-53"

2. **Navigate to JWT Templates**

   - Sidebar → **"JWT Templates"**
   - Click on **"Default"** template (or create custom)

3. **Configure Token Lifetime**

   ```
   Session Token Lifetime: 3600 seconds (1 hour)
   ```

   **Recommended Values:**

   - Development: `3600` (1 hour)
   - Staging: `1800` (30 minutes)
   - Production: `900` (15 minutes) with auto-refresh

4. **Save Changes**
   - Click "Save" or "Update Template"
   - Changes take effect immediately

### Method 2: Frontend Configuration

Update your React app's Clerk provider:

```typescript
// In your main App.tsx or index.tsx
import { ClerkProvider } from "@clerk/clerk-react";

<ClerkProvider
  publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY}
  appearance={appearance}
  // Configure session settings
  sessionTokenLifetime={3600} // 1 hour
>
  {children}
</ClerkProvider>;
```

### Method 3: Auto-Refresh Token Hook

Create a custom hook to automatically refresh tokens:

```typescript
// hooks/useAutoRefreshToken.ts
import { useAuth } from "@clerk/clerk-react";
import { useEffect } from "react";

export function useAutoRefreshToken(refreshIntervalMinutes = 50) {
  const { getToken } = useAuth();

  useEffect(() => {
    // Refresh token before expiry
    const interval = setInterval(async () => {
      try {
        await getToken({ skipCache: true });
        console.log("🔄 Token refreshed automatically");
      } catch (error) {
        console.error("❌ Token refresh failed:", error);
      }
    }, refreshIntervalMinutes * 60 * 1000);

    return () => clearInterval(interval);
  }, [getToken, refreshIntervalMinutes]);
}

// Usage in your app
function App() {
  useAutoRefreshToken(50); // Refresh every 50 minutes
  // ... rest of your app
}
```

### Method 4: Backend Grace Period

Add leeway to your backend JWT verification:

```python
# app/auth/unified_auth.py or wherever you verify JWT

from datetime import timedelta

CLERK_JWT_OPTIONS = {
    "verify_signature": True,
    "verify_exp": True,
    "verify_nbf": True,
    "verify_iat": True,
    "verify_aud": False,
    "leeway": timedelta(seconds=60),  # Allow 60 seconds clock skew
}
```

## Testing Configuration

### Quick Test Token Retrieval

Add this to your React app temporarily:

```javascript
// Add to any component
useEffect(() => {
  const logToken = async () => {
    const token = await window.Clerk.session.getToken();
    console.log("🔑 Current JWT Token:", token);
    console.log("📅 Token will expire in ~1 hour");
  };
  logToken();
}, []);
```

### Browser Console Command

```javascript
// Run in browser console to get fresh token
const token = await window.Clerk.session.getToken({ skipCache: true });
console.log("Bearer " + token);
```

## Recommended Settings

| Environment | Token Lifetime | Auto-Refresh | Notes                        |
| ----------- | -------------- | ------------ | ---------------------------- |
| Development | 3600s (1h)     | Optional     | Easier testing               |
| Testing     | 1800s (30m)    | Recommended  | Balance security/convenience |
| Staging     | 900s (15m)     | Required     | Production-like              |
| Production  | 600s (10m)     | Required     | Maximum security             |

## Security Considerations

⚠️ **Important Notes:**

1. **Longer tokens = Higher risk** if compromised
2. **Always use HTTPS** in production
3. **Implement token refresh** instead of very long lifetimes
4. **Monitor token usage** in Clerk dashboard
5. **Rotate secrets regularly**

## Verification

After changing settings:

1. Get a new token from your app
2. Decode it at [jwt.io](https://jwt.io)
3. Check the `exp` (expiration) claim
4. Verify it matches your configured lifetime

```javascript
// Verify token expiration
const token = await window.Clerk.session.getToken();
const decoded = JSON.parse(atob(token.split(".")[1]));
const expiresAt = new Date(decoded.exp * 1000);
console.log("Token expires at:", expiresAt);
```

## Troubleshooting

### Token Still Expiring Quickly

- Clear browser cache
- Logout and login again
- Verify Clerk dashboard changes saved
- Check for multiple JWT templates

### Token Not Refreshing

- Verify `getToken({ skipCache: true })` is used
- Check network tab for refresh requests
- Ensure user session is still active

### Backend Still Rejecting Tokens

- Check server time synchronization
- Add leeway to JWT verification
- Verify Clerk public key is correct
- Check CORS configuration

## Current Token Info

Your current token details:

- **Issuer**: https://apt-clam-53.clerk.accounts.dev
- **Subject**: user_35jmaHb4A4gIjDtba9aZNIteFlnF
- **Organization**: org_35jmd7Lv317HzEZA68FeQRuk6Ol
- **Role**: admin
- **Default Expiry**: ~60 seconds (needs increase)

## Next Steps

1. ✅ Go to Clerk Dashboard
2. ✅ Increase token lifetime to 3600 seconds
3. ✅ Get a fresh token
4. ✅ Re-run your tests
5. ✅ Consider implementing auto-refresh for production
