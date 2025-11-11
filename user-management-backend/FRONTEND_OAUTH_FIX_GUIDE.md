# Frontend OAuth Fix Guide

## Issue Analysis

After examining the frontend OAuth implementation in `/home/cis/Music/Autogenlabs-Web-App`, I've identified the root cause of the redirect loop issue:

### Current Implementation Issues

1. **Missing Backend OAuth Endpoint**: The frontend callback page (`/auth/callback/page.jsx`) tries to call `/api/auth/exchange-code` which doesn't exist in the backend.

2. **Incorrect OAuth Flow**: The frontend is trying to implement its own OAuth flow instead of using the backend's OAuth implementation.

3. **Token Handling**: The frontend has complex logic for handling authorization codes, but the backend already handles this correctly.

## Solution

The backend OAuth implementation is working correctly (as confirmed by our tests). The frontend should simply:

1. **Use Backend OAuth Login**: Redirect users to backend OAuth login endpoint
2. **Handle Callback**: Process tokens from backend callback
3. **Store Tokens**: Save tokens in localStorage
4. **Update Auth State**: Set authentication state
5. **Redirect to Dashboard**: Navigate away from auth pages

## Implementation Steps

### Step 1: Update OAuth Login Button

Replace the current OAuth login implementation with a simple redirect to the backend:

```jsx
// In your AuthForm component or wherever you have the Google login button
<button
  onClick={() => window.location.href = 'http://localhost:8000/api/auth/google/login'}
  className="w-full flex items-center justify-center gap-2 bg-white/10 hover:bg-gray-50 text-gray-900 px-4 py-3 rounded-lg shadow-sm transition-colors duration-300"
>
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
    <path d="M22.56 12.25c0-1.097-.652 1.706-1.814 1.706h2.268c0-1.097.652-.652-1.706-1.814-1.706H5.484c0-1.097.652-.652-1.706-1.814-1.706A17.652 17.652c0 1.097.652.652 1.706 1.814 1.706h-2.268c0-1.097-.652-1.706-1.814-1.706A17.652 17.652c0 1.097.652.652 1.706 1.814 1.706z"/>
  </svg>
  <span className="text-sm font-medium">Continue with Google</span>
</button>
```

### Step 2: Simplify OAuth Callback Page

Replace the entire `/home/cis/Music/Autogenlabs-Web-App/src/app/auth/callback/page.jsx` with this simplified version:

```jsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '../../../contexts/AuthContext';

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('');
  
  useEffect(() => {
    // Get tokens from URL parameters
    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    const userId = searchParams.get('user_id');
    const error = searchParams.get('error');
    
    console.log('OAuth callback params:', { accessToken, refreshToken, userId, error });
    
    if (error) {
      setStatus('error');
      setMessage(`Authentication error: ${error}`);
      setTimeout(() => router.push('/auth'), 3000);
      return;
    }
    
    if (accessToken && refreshToken && userId) {
      // Store tokens in localStorage
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      localStorage.setItem('user_id', userId);
      
      // Update auth context
      login({
        id: userId,
        accessToken,
        refreshToken
      });
      
      setStatus('success');
      setMessage('Authentication successful! Redirecting to dashboard...');
      
      // Redirect to dashboard after successful authentication
      setTimeout(() => {
        router.push('/dashboard');
      }, 1500);
    } else {
      setStatus('error');
      setMessage('No authentication tokens received');
      setTimeout(() => router.push('/auth'), 3000);
    }
  }, [searchParams, router, login]);
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900">
      <div className="max-w-md w-full space-y-8 p-8 bg-white/10 backdrop-blur-sm rounded-lg shadow-xl">
        <div className="text-center">
          <div className="mb-8">
            <div className={`mx-auto h-12 w-12 rounded-full flex items-center justify-center ${status === 'loading' ? 'bg-blue-600' : status === 'success' ? 'bg-green-600' : 'bg-red-600'}`}>
              {status === 'loading' && (
                <div className="animate-spin rounded-full h-8 w-8 border-b-4 border-white"></div>
              )}
              {status === 'success' && (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L4 4L4 4M6 11l-4-4-4-4M4 4v6m0 6h4m0 6v6m0 6h4"/>
                </svg>
              )}
              {status === 'error' && (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
                </svg>
              )}
            </div>
          </div>
          
          <h2 className={`text-2xl font-bold mb-4 ${status === 'success' ? 'text-green-600' : status === 'error' ? 'text-red-600' : 'text-gray-900'}`}>
            {status === 'loading' && 'Processing...'}
            {status === 'success' && 'Authentication Successful!'}
            {status === 'error' && 'Authentication Failed'}
          </h2>
          
          <p className={`text-center mb-8 ${status === 'success' ? 'text-green-600' : status === 'error' ? 'text-red-600' : 'text-gray-600'}`}>
            {message}
          </p>
          
          {status === 'error' && (
            <button
              onClick={() => router.push('/auth')}
              className="w-full text-center py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-300"
            >
              Back to Login
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
```

### Step 3: Update Auth Context

Make sure your AuthContext properly handles the authentication state:

```jsx
// In your contexts/AuthContext.js
import React, { createContext, useContext, useEffect, useState } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  useEffect(() => {
    // Check for existing tokens on mount
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const userId = localStorage.getItem('user_id');
    
    if (accessToken && refreshToken && userId) {
      setUser({ id: userId, accessToken, refreshToken });
      setIsAuthenticated(true);
    }
  }, []);
  
  const login = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('access_token', userData.accessToken);
    localStorage.setItem('refresh_token', userData.refreshToken);
    localStorage.setItem('user_id', userData.id);
  };
  
  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
  };
  
  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Step 4: Add Route Protection

Create a simple AuthGuard component to protect routes:

```jsx
// In components/AuthGuard.jsx
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function AuthGuard({ children }) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, router]);
  
  if (!isAuthenticated) {
    return null; // or loading spinner
  }
  
  return children;
}
```

### Step 5: Update App Layout

Wrap your app with AuthProvider and protect routes:

```jsx
// In your app/layout.jsx or _app.jsx
import { AuthProvider } from '../contexts/AuthContext';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

## Testing the Fix

1. **Start Backend**: Ensure your backend is running on port 8000
2. **Clear Browser Storage**: Clear localStorage to test fresh authentication
3. **Test OAuth Flow**: 
   - Go to `/auth` page
   - Click "Continue with Google"
   - Complete Google authentication
   - Verify you're redirected to dashboard

## Why This Fix Works

1. **Simplified Flow**: Removes complex frontend OAuth logic that was causing issues
2. **Backend Handles OAuth**: Leverages the working backend OAuth implementation
3. **Proper Token Handling**: Correctly extracts and stores tokens from callback
4. **No Redirect Loops**: Proper authentication state management prevents loops
5. **Better UX**: Clear loading states and error handling

## Files to Modify

1. `/home/cis/Music/Autogenlabs-Web-App/src/app/auth/callback/page.jsx` - Replace with simplified version
2. `/home/cis/Music/Autogenlabs-Web-App/src/contexts/AuthContext.js` - Update or create
3. `/home/cis/Music/Autogenlabs-Web-App/src/components/AuthGuard.jsx` - Create route protection
4. `/home/cis/Music/Autogenlabs-Web-App/src/app/layout.jsx` - Wrap with AuthProvider
5. Any login form components - Update to use backend OAuth login

## Alternative: Quick Fix

If you want a quick fix without major refactoring, just update the OAuth login button to redirect to the backend:

```jsx
// Replace your Google OAuth button with this:
<button
  onClick={() => window.location.href = 'http://localhost:8000/api/auth/google/login'}
  className="your-button-styles"
>
  Sign in with Google
</button>
```

This will use the backend's working OAuth implementation and immediately fix the redirect loop issue.