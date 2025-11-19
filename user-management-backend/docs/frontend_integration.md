# Frontend Integration Guide

This document summarizes everything the Next.js frontend needs in order to authenticate with Clerk, talk to the FastAPI backend, and surface the right API-key information to end users.

## 1. Prerequisites & Environment

| Purpose | Variable | Notes |
| --- | --- | --- |
| Backend base URL | `NEXT_PUBLIC_BACKEND_URL` | Defaults to `http://localhost:8000` for local dev. |
| Clerk publishable key | `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Already required by `@clerk/nextjs`. |
| Clerk secret key (server) | `CLERK_SECRET_KEY` | Needed on Next.js server routes. |
| Clerk JWT template | `CLERK_JWT_TEMPLATE` (optional) | Use if you need longer-lived tokens, as shown in `frontend_clerk_token_config.ts`. |

Install `@clerk/nextjs` and ensure all protected pages/components are wrapped with Clerk providers so `getToken()` is available both on the client and server.

## 2. Authenticating Requests

1. **Client-side verification** (see `frontend_client_helper.js`):
   - Call `getToken()` from `@clerk/nextjs`.
   - POST the token to `POST /api/verify-user` with `{ token }`.
   - The backend responds with `{ verified: true, user, claims }`.

2. **Server-side (Next.js Route Handler) example** (`frontend_api_route_example.ts`):
   - Use `auth()` from `@clerk/nextjs/server` to ensure the session is present.
   - Fetch `GET /api/users/me` with the bearer token to hydrate the frontend with profile + key data.

### Minimal helper (client)
```ts
import { getToken } from "@clerk/nextjs";

export async function fetchWithAuth(path: string, init: RequestInit = {}) {
  const token = await getToken();
  if (!token) throw new Error("Missing Clerk token");

  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}${path}`, {
    ...init,
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
```

## 3. User Profile & API Keys (`GET /api/users/me`)
The backend returns a unified profile that includes:
- `openrouter_api_key` (string | null): Auto-provisioned per-user OpenRouter key. Returns `null` if `OPENROUTER_PROVISIONING_API_KEY` is not configured in backend `.env`.
- `glm_api_key` (string | null): User-provided GLM key, only for paid/whitelisted plans.
- `api_keys` (array): Legacy user-created API keys (typically empty for most users).
- Capability booleans (create components, templates, etc.).

**Note**: Managed API keys are accessed via separate endpoints (see section 5).

Call this endpoint after every login to keep local state up to date.

### Response Example
```json
{
  "id": "691d926bf9dbddfa0ec7837a",
  "email": "user@example.com",
  "is_active": true,
  "openrouter_api_key": "sk-or-v1-abc123...",
  "glm_api_key": null,
  "api_keys": [],
  "role": "user",
  "can_publish_content": true
}
```

## 4. GLM Key Handling (Paid Users Only)
- Endpoint: `POST /api/users/me/glm-api-key?api_key=...`
- Requires authenticated token **and** the backend-verified plan flag (subscription must be "pro" or "enterprise").
- Returns the key as a string in the response body.
- Use the helper in `frontend_glm_setup.ts` to automatically push the user's GLM key once they upgrade.

**Note**: Unlike `api_keys` (which is an array), `glm_api_key` is returned as a **string** (or `null`).

## 5. Managed API Keys
- **Read current key:** already included in `GET /api/users/me`.
- **Force rotation:** `POST /api/users/me/managed-api-key/refresh` (body empty). Backend issues a fresh managed key and returns updated profile payload.
- Handle 429s by disabling the rotate button until the Promise settles.

## 6. OpenRouter Keys
- Keys are auto-created at login, but the user can manually refresh.
- **Refresh endpoint**: `POST /api/users/me/openrouter-key/refresh`
- Returns: `{ "openrouter_api_key": "sk-or-v1-..." }`
- UI suggestion: show the `openrouter_api_key` and provide a "Regenerate" button that calls the refresh endpoint and replaces the locally cached key.

### Example Usage
```typescript
// Refresh OpenRouter key
const response = await fetchWithAuth('/api/users/me/openrouter-key/refresh', {
  method: 'POST'
});
// response = { "openrouter_api_key": "sk-or-v1-..." }
```

## 7. Admin-Only Screens (optional)
If the frontend exposes admin dashboards, target the namespaced routes (note the `/api` prefix):
- `GET /api/admin/managed-api-keys?limit=50` – list keys in the pool with status info.
- `POST /api/admin/managed-api-keys` – bulk add new keys. Body: `{ "keys": ["key1", "key2"], "label": "OpenRouter seat" }`.
- `POST /api/admin/users/{user_id}/managed-api-key/refresh` – issue a replacement key for a specific user.

These routes require the acting Clerk user to have the admin org role; make sure the frontend defers rendering unless the Clerk org role is `admin`.

## 8. Common Pitfalls
- **Missing `/api` prefix**: Admin requests hitting `/admin/...` will 404; always call `/api/admin/...`.
- **Token template mismatch**: If `getToken()` returns `null`, ensure the component is wrapped in `<ClerkProvider>` and the user is signed in.
- **CORS in local dev**: Keep the backend running via Docker (`docker compose up api redis mongodb`). For Next.js API routes, consider proxying through `/api/*` to avoid cross-origin issues.
- **`openrouter_api_key` is null**: Check that `OPENROUTER_PROVISIONING_API_KEY` is set in the backend `.env` file. Without this key, the backend cannot provision per-user OpenRouter keys. Add it like:
  ```bash
  OPENROUTER_PROVISIONING_API_KEY=sk-or-v1-your-admin-provisioning-key
  ```
  Then restart the API container: `docker compose restart api`

## 9. Recommended Flow
1. On app mount, verify the session using `verifyUserWithClerk`.
2. Fetch `/api/users/me` and store `managed_api_key`, `openrouter_api_key`, and capabilities in context.
3. Present a settings screen where users can:
   - Paste their GLM key (if applicable) → call GLM endpoint.
   - Regenerate their managed/OpenRouter keys → call the refresh endpoints.
4. For admin dashboards, fetch `/api/admin/managed-api-keys` to monitor pool health.

With these pieces wired up, the frontend can safely orchestrate user auth, API-key distribution, and admin workflows entirely through the documented endpoints.
