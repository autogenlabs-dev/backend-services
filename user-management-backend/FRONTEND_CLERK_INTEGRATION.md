**Frontend → Backend (Clerk) Integration Guide**

This file describes how the frontend (Next.js / React using Clerk) should interact with the backend API implemented in this repository. It includes code snippets, environment variables, testing steps, and troubleshooting tips to get a working Clerk→backend integration quickly.

**Overview**:
- Frontend obtains a Clerk session token (recommended via Clerk SDK `getToken()`).
- Frontend includes the token in the `Authorization: Bearer <token>` header when calling protected backend endpoints.
- Backend verifies the token using JWKS (configured via `CLERK_JWKS_URL` and `CLERK_ISSUER`).
- A dev-only endpoint `/api/debug/verify-clerk` exists to inspect claims when `DEBUG=True`.

**Files/Endpoints (backend)**
- `POST /api/debug/verify-clerk` — Dev-only. Accepts JSON `{ "token": "..." }` and returns parsed claims. Ensure backend `DEBUG` is enabled for local testing.
- Any protected endpoint (example): `GET /api/users/me` — requires `Authorization: Bearer <token>`.

**Environment variables (backend)**
- `CLERK_JWKS_URL` — URL to your Clerk instance JWKS (example: `https://apt-clam-53.clerk.accounts.dev/.well-known/jwks.json`).
- `CLERK_ISSUER` — issuer URL used by Clerk tokens (example: `https://apt-clam-53.accounts.dev`).
- `CLERK_AUDIENCE` — optional; set if your tokens include an `aud` claim that must be validated.

**Recommended Frontend Implementation (Next.js w/ Clerk v5)**

1) Install Clerk as usual in your frontend project (if not already):

```bash
npm install @clerk/nextjs
```

2) Use `getToken()` when making server requests — example component:

```js
import { useAuth } from '@clerk/nextjs'

export default function CallApiButton() {
  const { getToken } = useAuth();

  async function callApi() {
    try {
      const token = await getToken();
      const res = await fetch('http://localhost:8000/api/users/me', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        }
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`API ${res.status}: ${text}`);
      }

      const data = await res.json();
      console.log('Profile', data);
    } catch (err) {
      console.error('API call failed', err);
    }
  }

  return <button onClick={callApi}>Call protected API</button>;
}
```

3) Server-side calls (optional): If you need to call the backend from Next.js server routes, prefer the Clerk server SDK on your backend or pass the token from the client to the server-route and forward it to the backend.

**Quick Local Tests**

1. Use the debug verifier (dev only):

```bash
# Verify a token and view claims (replace <TOKEN>)
curl -X POST http://localhost:8000/api/debug/verify-clerk \
  -H "Content-Type: application/json" \
  -d '{"token":"<TOKEN>"}'
```

2. Call protected endpoint:

```bash
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/users/me
```

**If you see errors**
- `401 Invalid token header` — token is malformed. Use Clerk SDK `getToken()` instead of reading localStorage directly.
- `401 Invalid token issuer` — set `CLERK_ISSUER` to the token `iss` value from Clerk (exact match required).
- `401 Invalid token audience` — set `CLERK_AUDIENCE` to the expected `aud` claim, or leave unset if you do not validate `aud`.
- `503 Unable to fetch JWKS` — backend cannot reach the `CLERK_JWKS_URL`. Ensure network access and correct URL.

**Security Notes**
- Prefer short-lived Clerk session tokens obtained via the Clerk SDK.
- Do not read Clerk tokens from localStorage in production; use Clerk SDK functions which respect session rules and rotate tokens correctly.
- Never expose secret keys (e.g., Clerk server API keys) to the browser. If you need server-side user introspection, use server-side Clerk SDK on your backend with a secret.

**Optional: Exchange flow (frontend → backend ticket)**
- If your frontend needs a short-lived backend ticket (extension/ticket flow), implement a backend endpoint `/api/extension/clerk-to-ticket` that accepts a Clerk token, verifies it server-side, and issues your backend ticket. This repo has placeholders for extension flows that can be extended.

**Example flow:**
1. Frontend obtains token via `getToken()`.
2. Frontend POSTs token to `/api/extension/clerk-to-ticket`.
3. Backend verifies via JWKS and, if valid, creates an extension ticket in Redis and returns it to the frontend.

**Troubleshooting Checklist for Frontend Team**
- Confirm Clerk SDK `getToken()` returns a non-empty string in dev console.
- Use the debug endpoint to inspect claims and confirm `iss` and `aud`.
- Confirm backend `CLERK_JWKS_URL` and `CLERK_ISSUER` match your Clerk instance.
- If CORS issues occur, add the frontend origin to backend `backend_cors_origins` setting.

**Where to look in this repo**
- Backend verifier: `app/auth/clerk_verifier.py`
- Unified auth dependency: `app/auth/unified_auth.py`
- Dev debug endpoint: `app/api/debug.py`
- Compose defaults: `docker-compose.yml` (contains `CLERK_JWKS_URL` and `CLERK_ISSUER` placeholders)

----
If you want, I can also add a small Next.js example page inside the frontend repo with the exact `getToken()` usage and an automated test that calls `/api/users/me`. Tell me if you want that and which frontend repo path to modify.
