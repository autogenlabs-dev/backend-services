import { NextResponse } from 'next/server'
import { auth, currentUser } from '@clerk/nextjs/server'

export async function GET(request: Request) {
  try {
    // Verify Clerk session
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
    }

    // Get the Clerk token
    const { getToken } = await import('@clerk/nextjs')
    const token = await getToken()

    if (!token) {
      return NextResponse.json({ error: 'No token available' }, { status: 401 })
    }

    // Call backend to get user profile (which includes API keys)
    const response = await fetch('http://localhost:8000/api/users/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || 'Failed to get user data' },
        { status: response.status }
      )
    }

    // Return the API keys from the user profile
    return NextResponse.json({
      api_keys: data.api_keys || [],
      user: {
        id: data.id,
        email: data.email,
        is_active: data.is_active
      }
    })
  } catch (err) {
    console.error('API key fetch error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}