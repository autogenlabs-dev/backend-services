# OpenRouter Provisioning Setup

## Issue
The `/api/users/me` endpoint returns `openrouter_api_key: null` because the backend cannot provision per-user OpenRouter keys.

## Root Cause
The `OPENROUTER_PROVISIONING_API_KEY` environment variable is missing from your `.env` file.

## Solution

### 1. Obtain OpenRouter Provisioning Key
Contact OpenRouter support or check your OpenRouter dashboard for a **provisioning API key** (not a regular API key). This special key allows your backend to create per-user API keys programmatically.

The provisioning key should look like:
```
sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. Add to Environment File
Open `/home/cis/Music/backend-services/user-management-backend/.env` and add:

```bash
OPENROUTER_PROVISIONING_API_KEY=sk-or-v1-your-actual-provisioning-key-here
```

### 3. Restart API Container
```bash
cd /home/cis/Music/backend-services/user-management-backend
docker compose restart api
```

### 4. Verify
After restart, log in again (or hit the refresh endpoint) and check `/api/users/me`:

```bash
# Get a fresh Clerk token from your frontend
curl -H "Authorization: Bearer YOUR_CLERK_TOKEN" \
  http://localhost:8000/api/users/me
```

Expected response:
```json
{
  "id": "...",
  "email": "user@example.com",
  "openrouter_api_key": "sk-or-v1-abc123...",
  "glm_api_key": null,
  ...
}
```

## How It Works
- On login (`update_user_last_login`), the backend calls `ensure_user_openrouter_key(user)`.
- If `user.openrouter_api_key` is `null`, it makes a POST request to `https://openrouter.ai/api/v1/keys` using the provisioning key.
- The provisioned key is stored in `user.openrouter_api_key` and returned in `/api/users/me`.

## Manual Refresh
Users can also manually refresh their OpenRouter key via:
```
POST /api/users/me/openrouter-api-key/refresh
```

## Troubleshooting
- **Still null after restart?** Check Docker logs: `docker compose logs api | grep -i openrouter`
- **404 or 5xx from OpenRouter?** Verify the provisioning key is valid and has the correct permissions.
- **Key provisioned but frontend doesn't show it?** Ensure the frontend calls `/api/users/me` (not `/users/me`) with the correct bearer token.
