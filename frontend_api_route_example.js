import { NextRequest, NextResponse } from 'next/server';
import { getToken } from '@clerk/nextjs/server';

export async function GET(request: NextRequest) {
  try {
    // Get the Clerk JWT token
    const token = await getToken({ template: 'your-template-name' }); // Use your actual template name

    if (!token) {
      return NextResponse.json(
        { error: 'No authentication token found' },
        { status: 401 }
      );
    }

    // Backend URL - adjust this to match your backend deployment
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    // Forward the request to backend /api/users/me
    const response = await fetch(`${backendUrl}/api/users/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Backend request failed' }));
      return NextResponse.json(
        { error: errorData.error || 'Failed to fetch user data' },
        { status: response.status }
      );
    }

    const userData = await response.json();

    // Return the API keys from the user profile
    return NextResponse.json({
      api_keys: userData.api_keys || []
    });

  } catch (error) {
    console.error('API key retrieval error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}