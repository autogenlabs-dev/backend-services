import { NextResponse } from 'next/server'
import { auth, currentUser } from '@clerk/nextjs/server'

export async function POST(request: Request) {
  try {
    // Read Clerk auth from the incoming request (requires browser cookies)
    const { userId, sessionId } = await auth()

    if (!userId) {
      return NextResponse.json({ error: 'Not authenticated (no Clerk session). Make sure you call this from a browser with an active Clerk session.' }, { status: 401 })
    }

    const user = await currentUser()

    // Read the token from the request body
    const body = await request.json()
    const { token } = body

    if (!token) {
      return NextResponse.json({ error: 'Token is required in request body' }, { status: 400 })
    }

    // Call backend to verify the token
    const resp = await fetch('http://localhost:8000/api/verify-user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    })

    const text = await resp.text()
    let backendBody: any
    try {
      backendBody = JSON.parse(text)
    } catch (e) {
      backendBody = { data: text }
    }

    return NextResponse.json({
      ok: resp.ok,
      status: resp.status,
      backendBody,
      clerk: { userId, sessionId, user }
    })
  } catch (err) {
    return NextResponse.json({ error: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 })
  }
}