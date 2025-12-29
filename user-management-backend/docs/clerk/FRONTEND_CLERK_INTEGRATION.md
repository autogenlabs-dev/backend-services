# Frontend Clerk Authentication Integration

## Overview

The backend API now properly validates Clerk JWT tokens. The frontend needs to send the Clerk session token with every API request to authenticate users.

## Required Changes

### 1. Update API Client (`src/lib/api.js`)

Add this helper function after the `handleApiResponse` function (around line 35):

```javascript
/**
 * Helper function to make authenticated API requests
 * Automatically includes Clerk token if provided
 */
export const apiRequest = async (endpoint, options = {}, token = null) => {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    // Add Clerk token if provided
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });
    
    return handleApiResponse(response);
};
```

### 2. Create Custom Hook (`src/hooks/useApi.js`)

Create a new file with this content:

```javascript
import { useAuth } from '@clerk/nextjs';
import { useCallback } from 'react';
import { apiRequest } from '@/lib/api';

/**
 * Custom hook for making authenticated API requests
 * Automatically includes Clerk session token
 */
export const useApi = () => {
    const { getToken } = useAuth();
    
    const makeRequest = useCallback(async (endpoint, options = {}) => {
        // Get Clerk session token
        const token = await getToken();
        
        // Make request with token
        return apiRequest(endpoint, options, token);
    }, [getToken]);
    
    return { makeRequest };
};
```

### 3. Update Components

Replace direct fetch calls with the `useApi` hook.

**Before:**
```javascript
const response = await fetch(`${API_BASE_URL}/api/templates`, {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
    },
});
const data = await response.json();
```

**After:**
```javascript
import { useApi } from '@/hooks/useApi';

function MyComponent() {
    const { makeRequest } = useApi();
    
    const loadTemplates = async () => {
        try {
            const data = await makeRequest('/api/templates', {
                method: 'GET',
            });
            // Use data
        } catch (error) {
            console.error('API error:', error);
        }
    };
    
    // ... rest of component
}
```

### 4. Update Existing API Functions

Modify template API functions to use the token parameter:

**Example - Update `templateApi.createTemplate`:**

```javascript
export const templateApi = {
    async createTemplate(templateData, token) {
        return apiRequest('/templates', {
            method: 'POST',
            body: JSON.stringify(templateData),
        }, token);
    },
    
    async getAllTemplates(params = {}) {
        const queryParams = new URLSearchParams();
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
                queryParams.append(key, params[key]);
            }
        });
        
        const endpoint = `/templates${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        return apiRequest(endpoint, { method: 'GET' });
    },
    
    async getMyTemplates(params = {}, token) {
        const queryParams = new URLSearchParams();
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                queryParams.append(key, params[key]);
            }
        });
        
        const endpoint = `/templates/user/my-templates${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        return apiRequest(endpoint, { method: 'GET' }, token);
    },
    
    // Update other methods similarly...
};
```

**Then in components:**

```javascript
import { useApi } from '@/hooks/useApi';
import { templateApi } from '@/lib/api';

function CreateTemplate() {
    const { getToken } = useAuth();
    
    const handleSubmit = async (formData) => {
        const token = await getToken();
        const result = await templateApi.createTemplate(formData, token);
        // Handle result
    };
}
```

## Testing

### Browser Console Test

1. Open browser DevTools on `http://localhost:3000`
2. Sign in with Clerk
3. Run this in the console:

```javascript
// Test authentication
const testAuth = async () => {
    const { useAuth } = await import('@clerk/nextjs');
    const token = await useAuth().getToken();
    
    const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    const data = await response.json();
    console.log('User data:', data);
};

testAuth();
```

Expected response:
```json
{
    "id": "user_xxx",
    "email": "user@example.com",
    "is_active": true,
    "created_at": "2025-11-16T...",
    ...
}
```

### Network Tab Verification

1. Open DevTools > Network tab
2. Make an API call from your app
3. Click on the request
4. Check Headers section
5. Verify `Authorization: Bearer eyJ...` is present

## Environment Variables

Ensure `.env.local` has:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2JA
CLERK_SECRET_KEY=sk_test_FtxbYvBnDrtJ7ajXTT0N8ehm3iQxNK1DYaCOY1jEhu
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Backend Endpoints

All authenticated endpoints now accept Clerk JWT tokens:

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/auth/me` | GET | Yes | Get current user info |
| `/api/templates` | GET | No | List all templates |
| `/api/templates` | POST | Yes | Create template |
| `/api/templates/{id}` | GET | No | Get template by ID |
| `/api/templates/{id}` | PUT | Yes | Update template |
| `/api/templates/{id}` | DELETE | Yes | Delete template |
| `/api/templates/user/my-templates` | GET | Yes | Get user's templates |
| `/api/admin/*` | * | Yes (Admin) | Admin endpoints |
| `/api/payments/*` | * | Yes | Payment endpoints |

## Error Handling

Handle 401 errors to redirect to sign-in:

```javascript
const { makeRequest } = useApi();

try {
    const data = await makeRequest('/api/protected-endpoint', {
        method: 'GET',
    });
} catch (error) {
    if (error.status === 401) {
        // Token invalid or expired - redirect to sign in
        router.push('/sign-in');
    } else {
        console.error('API error:', error.message);
    }
}
```

## Common Issues

### Issue: 401 Unauthorized

**Cause:** Token not being sent or invalid

**Solution:**
1. Check `Authorization` header is present in Network tab
2. Verify user is signed in with Clerk
3. Check token in console: `await getToken()`

### Issue: CORS Error

**Cause:** Missing or incorrect CORS headers

**Solution:** Backend already configured. Ensure you're using `http://localhost:3000` for frontend.

### Issue: Token Expired

**Cause:** Clerk token has expired

**Solution:** Clerk automatically refreshes tokens. If issue persists, sign out and sign in again.

## Backend Status

✅ **Backend is ready** - All fixes applied:
- Proper JWKS verification
- Clerk environment variables configured
- CORS properly set up
- Docker containers configured

The backend will automatically:
1. Verify Clerk JWT signature
2. Create user if doesn't exist
3. Update last login time
4. Return user data

## Questions?

Backend API is running at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`
