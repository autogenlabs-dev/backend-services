// Configure Clerk to use a template with longer expiration

import { useAuth } from '@clerk/nextjs';

export async function getClerkToken() {
  const { getToken } = useAuth();
  
  // Option 1: Use a specific JWT template with longer expiration
  const token = await getToken({ template: 'your-template-name' });
  
  // Option 2: Get session token directly (uses default template)
  // const token = await getToken();
  
  return token;
}

// Example: Use this in your API calls
export async function callBackendAPI(endpoint: string, options = {}) {
  const token = await getClerkToken();
  
  const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    }
  });
  
  return response.json();
}

// Usage examples:
/*
// Get user profile
const profile = await callBackendAPI('/api/users/me');

// Set GLM API key
const result = await callBackendAPI(
  '/api/users/me/glm-api-key?api_key=YOUR_GLM_API_KEY_HERE',
  { method: 'POST' }
);
*/
