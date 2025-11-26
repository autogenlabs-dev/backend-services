// Frontend code to set GLM API key automatically on login

import { useAuth } from '@clerk/nextjs';

export async function setUserGlmApiKey(glmApiKey: string) {
  const { getToken } = useAuth();
  const token = await getToken();

  if (!token) {
    console.error('No auth token available');
    return null;
  }

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/users/me/glm-api-key?api_key=${encodeURIComponent(glmApiKey)}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      }
    );

    const data = await response.json();
    console.log('GLM API key set:', data);
    return data;
  } catch (error) {
    console.error('Error setting GLM API key:', error);
    return null;
  }
}

// Usage: Call this after user logs in or on app mount
// Example in a useEffect:
/*
useEffect(() => {
  if (user) {
    setUserGlmApiKey('YOUR_GLM_API_KEY_HERE');
  }
}, [user]);
*/
