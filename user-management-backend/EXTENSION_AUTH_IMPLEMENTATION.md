# Codemurf Extension Authentication Implementation

## Overview

This document describes the implementation of Clerk-compatible authentication endpoints for the Codemurf VS Code extension. The extension expects specific API endpoints that mimic Clerk's authentication flow, and this implementation provides those endpoints using our own JWT-based system.

## Architecture

### Extension Authentication Flow

```
1. Extension calls CloudService.login()
   └─> Opens browser to: https://api.codemurf.com/extension/sign-in?state={state}&auth_redirect={vscode://publisher.extension}

2. Backend (/extension/sign-in)
   └─> Stores auth_redirect in Redis with state
   └─> Redirects to Google OAuth

3. Google OAuth
   └─> User authenticates
   └─> Redirects to: https://api.codemurf.com/api/auth/google/callback?code={google_code}&state={state}

4. Backend (/api/auth/google/callback)
   └─> Exchanges Google code for user info
   └─> Creates/finds user in database
   └─> Generates internal "ticket"
   └─> Stores ticket in Redis
   └─> Redirects to: vscode://publisher.extension?code={ticket}&state={state}

5. Extension receives callback
   └─> Validates state matches
   └─> Calls: POST /v1/client/sign_ins with ticket

6. Backend (/v1/client/sign_ins)
   └─> Validates ticket
   └─> Generates long-lived client_token (1 year JWT)
   └─> Generates session_id
   └─> Returns: {response: {created_session_id}} with Authorization header containing client_token

7. Extension stores credentials
   └─> Saves client_token and session_id in VS Code secrets

8. Extension requests session JWT
   └─> Calls: POST /v1/client/sessions/{session_id}/tokens with client_token

9. Backend (/v1/client/sessions/{session_id}/tokens)
   └─> Validates client_token
   └─> Generates short-lived JWT (1 hour)
   └─> Returns: {jwt: "..."}

10. Extension uses JWT for API calls
    └─> All API requests include: Authorization: Bearer {jwt}
```

## Implemented Endpoints

### 1. `/extension/sign-in` (GET)

**Purpose**: Initiate OAuth flow from extension

**Parameters**:
- `state`: CSRF protection token (required)
- `auth_redirect`: VS Code URI to redirect back to (required)

**Flow**:
1. Stores `auth_redirect` with `state` in Redis (10 min TTL)
2. Redirects to Google OAuth

**Example**:
```
GET /extension/sign-in?state=abc123&auth_redirect=vscode://publisher.extension
```

### 2. `/api/auth/google/callback` (Updated)

**Purpose**: Handle Google OAuth callback

**Enhanced to support**:
- Extension flow (generates ticket)
- PKCE flow (for web apps)
- Traditional OAuth (direct token return)

**Extension Flow**:
1. Retrieves `extension:auth:{state}` from Redis
2. Exchanges Google code for user info
3. Creates/finds user
4. Generates ticket and stores in Redis (5 min TTL)
5. Redirects to `auth_redirect` with ticket

### 3. `/v1/client/sign_ins` (POST)

**Purpose**: Exchange ticket for client token and session ID (Clerk-compatible)

**Body** (Form data):
- `strategy`: "ticket" (required)
- `ticket`: Authorization ticket from callback (required)

**Response**:
```json
{
  "response": {
    "created_session_id": "session_abc123"
  }
}
```

**Headers**:
- `Authorization`: `Bearer {client_token}` (long-lived JWT)

### 4. `/v1/client/sessions/{session_id}/tokens` (POST)

**Purpose**: Create short-lived JWT from client token (Clerk-compatible)

**Headers**:
- `Authorization`: `Bearer {client_token}` (required)

**Response**:
```json
{
  "jwt": "eyJ..."
}
```

### 5. `/v1/me` (GET)

**Purpose**: Get user information (Clerk-compatible)

**Headers**:
- `Authorization`: `Bearer {client_token or jwt}` (required)

**Response**:
```json
{
  "response": {
    "id": "user_id",
    "first_name": null,
    "last_name": null,
    "email_addresses": [
      {
        "id": "user_id",
        "email_address": "user@example.com"
      }
    ],
    "primary_email_address_id": "user_id",
    "image_url": null,
    "public_metadata": {}
  }
}
```

### 6. `/v1/me/organization_memberships` (GET)

**Purpose**: Get organization memberships (Clerk-compatible)

**Headers**:
- `Authorization`: `Bearer {client_token}` (required)

**Response**:
```json
{
  "response": []
}
```

*Note: Currently returns empty array. Can be implemented when organization features are added.*

### 7. `/v1/client/sessions/{session_id}/remove` (POST)

**Purpose**: Logout/remove session (Clerk-compatible)

**Headers**:
- `Authorization`: `Bearer {client_token}` (required)

**Response**:
```json
{
  "response": {
    "removed": true
  }
}
```

## Token Types

### 1. Client Token
- **Type**: Long-lived JWT (1 year)
- **Purpose**: Persistent authentication for extension
- **Stored**: VS Code secrets
- **Payload**:
  ```json
  {
    "sub": "user_id",
    "email": "user@example.com",
    "type": "client"
  }
  ```

### 2. Session Token
- **Type**: Short-lived JWT (1 hour)
- **Purpose**: API access token
- **Refreshed**: Periodically by extension
- **Payload**:
  ```json
  {
    "sub": "user_id",
    "email": "user@example.com",
    "type": "session"
  }
  ```

## Redis Keys

### Extension Flow
- `extension:auth:{state}` - Stores auth_redirect and source
  - TTL: 10 minutes
  - Value: `{"auth_redirect": "vscode://...", "source": "extension", "created_at": "..."}`

- `extension:ticket:{ticket}` - Stores user data for ticket exchange
  - TTL: 5 minutes
  - Value: `{"user_id": "...", "email": "...", "created_at": "..."}`

- `extension:session:{session_id}` - Stores session data
  - TTL: 30 days
  - Value: `{"user_id": "...", "email": "...", "created_at": "..."}`

## Configuration

### Google OAuth Settings

**Client ID**: (Your Google OAuth Client ID)
**Client Secret**: (Your Google OAuth Client Secret)

**Authorized JavaScript origins**:
- `https://codemurf.com`
- `http://localhost:3000`

**Authorized redirect URIs**:
- `https://api.codemurf.com/api/auth/google/callback`
- `http://localhost:8000/api/auth/google/callback`

### Environment Variables

```bash
# In .env file
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://api.codemurf.com/api/auth/google/callback

# JWT Settings
JWT_SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Redis (required for storing tickets and sessions)
REDIS_URL=redis://localhost:6379
```

## Testing

### Manual Testing Flow

1. **Start the backend**:
   ```bash
   cd /home/cis/Downloads/backend-services/user-management-backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Test extension sign-in initiation**:
   ```bash
   # Generate a random state
   state=$(openssl rand -hex 16)
   
   # Open in browser
   http://localhost:8000/extension/sign-in?state=$state&auth_redirect=vscode://publisher.extension
   ```

3. **After Google OAuth callback**, you'll receive a ticket. Test ticket exchange:
   ```bash
   curl -X POST http://localhost:8000/v1/client/sign_ins \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "strategy=ticket&ticket=YOUR_TICKET_HERE"
   ```

4. **Test session token creation**:
   ```bash
   curl -X POST http://localhost:8000/v1/client/sessions/SESSION_ID/tokens \
     -H "Authorization: Bearer YOUR_CLIENT_TOKEN"
   ```

5. **Test user info**:
   ```bash
   curl http://localhost:8000/v1/me \
     -H "Authorization: Bearer YOUR_CLIENT_TOKEN"
   ```

### Integration Testing

Use the Codemurf extension:
1. Open VS Code
2. Click "Sign in with Codemurf"
3. Extension should open browser to `/extension/sign-in`
4. Complete Google OAuth
5. Extension should receive callback and exchange ticket
6. Extension should be signed in

## Extension Configuration

The extension expects these URLs based on your environment:

**Production**:
- Sign-in URL: `https://api.codemurf.com/extension/sign-in`
- Clerk Base URL: `https://api.codemurf.com` (for v1 endpoints)

**Development**:
- Sign-in URL: `http://localhost:8000/extension/sign-in`
- Clerk Base URL: `http://localhost:8000` (for v1 endpoints)

## Security Considerations

1. **State Validation**: All OAuth flows use CSRF state tokens
2. **Ticket Expiry**: Tickets expire in 5 minutes (one-time use)
3. **Session Expiry**: Sessions expire in 30 days
4. **Token Types**: Different JWTs for client vs session access
5. **Redis Storage**: Temporary data stored in Redis with TTL
6. **HTTPS**: Production must use HTTPS for all endpoints

## Migration Notes

### From Kilocode to Codemurf

1. **No extension code changes needed** - Extension continues to use same API flow
2. **Backend endpoints** - All new endpoints added in `extension_auth.py`
3. **URL updates** - Change configuration to point to Codemurf URLs
4. **Branding** - All references to "Kilocode" replaced with "Codemurf"

### Files Created/Modified

**New Files**:
- `/app/api/extension_auth.py` - All extension authentication endpoints

**Modified Files**:
- `/app/api/auth.py` - Updated Google callback to handle extension flow
- `/app/main.py` - Added extension_auth router

## Troubleshooting

### Extension can't connect to backend
- Check backend is running on correct port
- Verify Google OAuth credentials are configured
- Check Redis is running and accessible

### OAuth callback fails
- Verify redirect URI matches Google OAuth settings
- Check state token is valid in Redis
- Ensure Redis TTL hasn't expired

### Token exchange fails
- Verify ticket hasn't expired (5 min)
- Check user exists and is active
- Verify Redis contains ticket data

### Session token creation fails
- Verify client token is valid
- Check session exists in Redis
- Ensure user is still active

## Future Enhancements

1. **Organization Support**: Implement multi-tenancy with organizations
2. **Token Blacklist**: Add token revocation on logout
3. **Rate Limiting**: Add rate limits per user/endpoint
4. **Audit Logging**: Log all authentication events
5. **2FA Support**: Add two-factor authentication
6. **SSO Integration**: Support enterprise SSO providers

## API Documentation

Full OpenAPI documentation available at:
- Development: `http://localhost:8000/docs`
- Production: `https://api.codemurf.com/docs`

## Support

For issues or questions:
- GitHub: [codemurf/backend-services](https://github.com/codemurf/backend-services)
- Email: support@codemurf.com
