# 🔐 CodeMurf Authentication Implementation Guide

## Overview

This document outlines the authentication flow implementation for CodeMurf, migrating from Kilocode.ai to codemurf.com with custom backend integration.

---

## 🎯 Current vs Target Configuration

### Current (Kilocode)
- **Frontend:** `https://app.roocode.com` → `https://app.kilocode.ai`
- **Auth Provider:** `https://clerk.roocode.com`
- **Authentication:** Clerk-based OAuth flow

### Target (CodeMurf)
- **Frontend:** `https://app.codemurf.com` (from `/home/cis/Music/Autogenlabs-Web-App`)
- **Backend API:** `https://api.codemurf.com` (from `/home/cis/Downloads/backend-services/user-management-backend`)
- **Authentication:** Custom OAuth/JWT flow

---

## 📋 Files to Modify

### 1. Configuration Files

#### `/packages/cloud/src/config.ts`
**Purpose:** Central configuration for API URLs

**Current Code:**
```typescript
export const PRODUCTION_CLERK_BASE_URL = "https://clerk.roocode.com"
export const PRODUCTION_ROO_CODE_API_URL = "https://app.roocode.com"

export const getClerkBaseUrl = () => process.env.CLERK_BASE_URL || PRODUCTION_CLERK_BASE_URL
export const getRooCodeApiUrl = () => process.env.ROO_CODE_API_URL || PRODUCTION_ROO_CODE_API_URL
```

**New Code:**
```typescript
// kilocode_change start - Updated for CodeMurf
export const PRODUCTION_CODEMURF_API_URL = "https://api.codemurf.com"
export const PRODUCTION_CODEMURF_WEB_URL = "https://app.codemurf.com"

export const getCodeMurfApiUrl = () => process.env.CODEMURF_API_URL || PRODUCTION_CODEMURF_API_URL
export const getCodeMurfWebUrl = () => process.env.CODEMURF_WEB_URL || PRODUCTION_CODEMURF_WEB_URL

// Legacy Roo Code support (can be removed if not needed)
export const PRODUCTION_CLERK_BASE_URL = "https://clerk.roocode.com"
export const PRODUCTION_ROO_CODE_API_URL = "https://app.roocode.com"
export const getClerkBaseUrl = () => process.env.CLERK_BASE_URL || PRODUCTION_CLERK_BASE_URL
export const getRooCodeApiUrl = () => process.env.ROO_CODE_API_URL || PRODUCTION_ROO_CODE_API_URL
// kilocode_change end
```

---

### 2. Authentication Service

#### `/packages/cloud/src/WebAuthService.ts`

**Key Methods to Update:**

##### a. Login Method (Lines 256-287)
```typescript
// kilocode_change start - CodeMurf authentication
public async login(landingPageSlug?: string): Promise<void> {
    try {
        const vscode = await importVscode()
        if (!vscode) {
            throw new Error("VS Code API not available")
        }

        // Generate PKCE parameters for security
        const state = crypto.randomBytes(16).toString("hex")
        const codeVerifier = crypto.randomBytes(32).toString("base64url")
        const codeChallenge = crypto
            .createHash("sha256")
            .update(codeVerifier)
            .digest("base64url")

        // Store for callback verification
        await this.context.globalState.update(AUTH_STATE_KEY, state)
        await this.context.globalState.update("auth-code-verifier", codeVerifier)

        const packageJSON = this.context.extension?.packageJSON
        const publisher = packageJSON?.publisher ?? "codemurf"
        const name = packageJSON?.name ?? "codemurf-extension"

        const params = new URLSearchParams({
            state,
            code_challenge: codeChallenge,
            code_challenge_method: "S256",
            response_type: "code",
            redirect_uri: `${vscode.env.uriScheme}://${publisher}.${name}/auth-callback`,
            callbackPath: "/sign-in-to-editor", // Your backend parameter
        })

        // Use CodeMurf sign-in URL
        const url = `${getCodeMurfWebUrl()}/users/sign_in?${params.toString()}`

        await vscode.env.openExternal(vscode.Uri.parse(url))
    } catch (error) {
        this.log(`[auth] Error initiating CodeMurf auth: ${error}`)
        throw new Error(`Failed to initiate CodeMurf authentication: ${error}`)
    }
}
// kilocode_change end
```

##### b. Handle Callback Method
```typescript
// kilocode_change start - CodeMurf callback handler
public async handleCallback(
    code: string | null,
    state: string | null,
    organizationId?: string | null,
): Promise<void> {
    if (!code || !state) {
        const vscode = await importVscode()
        if (vscode) {
            vscode.window.showInformationMessage("Invalid CodeMurf sign in url")
        }
        return
    }

    try {
        // Validate state parameter (CSRF protection)
        const storedState = this.context.globalState.get(AUTH_STATE_KEY)
        if (state !== storedState) {
            this.log("[auth] State mismatch in callback")
            throw new Error("Invalid state parameter")
        }

        // Get code verifier for PKCE
        const codeVerifier = this.context.globalState.get("auth-code-verifier") as string

        // Exchange authorization code for tokens with CodeMurf backend
        const credentials = await this.exchangeCodeForTokens(code, codeVerifier)

        // Store credentials
        credentials.organizationId = organizationId || null
        await this.storeCredentials(credentials)

        const vscode = await importVscode()
        if (vscode) {
            vscode.window.showInformationMessage("Successfully authenticated with CodeMurf")
        }

        this.log("[auth] Successfully authenticated with CodeMurf")
    } catch (error) {
        this.log(`[auth] Error handling CodeMurf callback: ${error}`)
        this.changeState("logged-out")
        throw new Error(`Failed to handle CodeMurf callback: ${error}`)
    }
}
// kilocode_change end
```

##### c. Exchange Code for Tokens (New Method)
```typescript
// kilocode_change start - New method for CodeMurf token exchange
private async exchangeCodeForTokens(
    authorizationCode: string,
    codeVerifier: string
): Promise<AuthCredentials> {
    const response = await fetch(`${getCodeMurfApiUrl()}/auth/token`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "User-Agent": getUserAgent(),
        },
        body: JSON.stringify({
            grant_type: "authorization_code",
            code: authorizationCode,
            code_verifier: codeVerifier,
            redirect_uri: "vscode://codemurf.codemurf-extension/auth-callback",
        }),
    })

    if (!response.ok) {
        throw new Error(`Token exchange failed: ${response.statusText}`)
    }

    const data = await response.json()

    return {
        clientToken: data.access_token,
        sessionId: data.session_id || crypto.randomBytes(16).toString("hex"),
        organizationId: data.organization_id || null,
    }
}
// kilocode_change end
```

---

### 3. OAuth URLs

#### `/webview-ui/src/oauth/urls.ts`

**Add CodeMurf OAuth URL:**
```typescript
// kilocode_change start - CodeMurf OAuth
export function getCodeMurfAuthUrl(uriScheme?: string) {
    const callbackUrl = getCallbackUrl("codemurf", uriScheme)
    return `https://app.codemurf.com/users/sign_in?callbackPath=/sign-in-to-editor&callback_url=${callbackUrl}`
}
// kilocode_change end
```

---

### 4. Welcome View Integration

#### `/webview-ui/src/components/welcome/WelcomeView.tsx`

Update the provider list to include CodeMurf:

```typescript
// kilocode_change start - Add CodeMurf provider
const baseProviders = [
    {
        slug: "codemurf",
        name: "CodeMurf",
        description: t("welcome:routers.codemurf.description"),
        incentive: t("welcome:routers.codemurf.incentive"),
        authUrl: getCodeMurfAuthUrl(uriScheme),
    },
    {
        slug: "requesty",
        name: "Requesty",
        description: t("welcome:routers.requesty.description"),
        incentive: t("welcome:routers.requesty.incentive"),
        authUrl: getRequestyAuthUrl(uriScheme),
    },
    // ... other providers
]
// kilocode_change end
```

---

## 🔄 Authentication Flow

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     1. User Opens Extension                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         2. Check for Existing Authentication                │
│         - Check localStorage: 'kilocode_authenticated'      │
│         - Check stored credentials in extension context     │
└────────────────────┬────────────────────────────────────────┘
                     │
           ┌─────────┴─────────┐
           │                   │
           ▼ YES               ▼ NO
    ┌────────────┐      ┌─────────────┐
    │  Show Chat │      │Show Welcome │
    │    View    │      │ /Login Page │
    └────────────┘      └──────┬──────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │   3. User Clicks "Sign In"   │
                └──────────────┬───────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │   4. Extension Calls WebAuthService.login()   │
        │   - Generate state (CSRF protection)          │
        │   - Generate PKCE code_verifier & challenge   │
        │   - Store in extension context                │
        └──────────────────┬───────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │  5. Open Browser to CodeMurf Sign-In Page    │
        │  URL: https://app.codemurf.com/users/sign_in │
        │  Params:                                      │
        │    - state: [random hex]                      │
        │    - code_challenge: [sha256 hash]            │
        │    - code_challenge_method: S256              │
        │    - response_type: code                      │
        │    - redirect_uri: vscode://...               │
        │    - callbackPath: /sign-in-to-editor        │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │    6. User Authenticates on Web App          │
        │    - Email/password or social login          │
        │    - Backend validates credentials           │
        │    - Backend generates authorization code    │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │  7. Redirect Back to VS Code Extension       │
        │  URL: vscode://publisher.name/auth-callback  │
        │  Params:                                      │
        │    - code: [authorization_code]              │
        │    - state: [original state]                 │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │  8. Extension Handles Callback               │
        │  - Validate state matches                    │
        │  - Call exchangeCodeForTokens()              │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │  9. Exchange Code for Tokens                 │
        │  POST https://api.codemurf.com/auth/token    │
        │  Body:                                        │
        │    - grant_type: authorization_code          │
        │    - code: [authorization_code]              │
        │    - code_verifier: [stored verifier]        │
        │    - redirect_uri: vscode://...              │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │  10. Backend Validates & Returns Tokens      │
        │  Response:                                    │
        │    - access_token: [JWT]                     │
        │    - refresh_token: [JWT]                    │
        │    - session_id: [UUID]                      │
        │    - organization_id: [optional]             │
        │    - expires_in: [seconds]                   │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │  11. Store Credentials                       │
        │  - Save to extension context (secure)        │
        │  - Save 'kilocode_authenticated' = true      │
        │    to localStorage                           │
        │  - Update global authentication state        │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │  12. Show Success & Switch to Chat View      │
        │  - Display success message                   │
        │  - Update UI state                           │
        │  - User can now use extension                │
        └─────────────────────────────────────────────┘
```

---

## 🛡️ Security Considerations

### 1. **PKCE (Proof Key for Code Exchange)**
- Prevents authorization code interception attacks
- Uses SHA-256 hashing of code_verifier to create code_challenge
- Backend validates code_verifier during token exchange

### 2. **State Parameter**
- Prevents CSRF (Cross-Site Request Forgery) attacks
- Randomly generated and stored before redirect
- Validated when callback returns

### 3. **Token Storage**
- Access tokens stored in VS Code's secure storage (encrypted)
- Never expose tokens in logs or error messages
- Implement token refresh before expiration

### 4. **HTTPS Only**
- All authentication endpoints must use HTTPS
- Prevents man-in-the-middle attacks

---

## 📡 Backend API Requirements

Your backend at `https://api.codemurf.com` needs these endpoints:

### 1. **Authorization Endpoint**
```
GET https://app.codemurf.com/users/sign_in
```
**Query Parameters:**
- `state`: CSRF protection token
- `code_challenge`: SHA-256 hash of code_verifier
- `code_challenge_method`: "S256"
- `response_type`: "code"
- `redirect_uri`: VS Code callback URI
- `callbackPath`: "/sign-in-to-editor"

**Response:**
- Redirect to `redirect_uri` with:
  - `code`: authorization code
  - `state`: original state parameter

---

### 2. **Token Exchange Endpoint**
```
POST https://api.codemurf.com/auth/token
Content-Type: application/json
```

**Request Body:**
```json
{
  "grant_type": "authorization_code",
  "code": "authorization_code_from_callback",
  "code_verifier": "original_code_verifier",
  "redirect_uri": "vscode://publisher.name/auth-callback"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "session_id": "uuid-v4-here",
  "organization_id": "org-123-optional"
}
```

---

### 3. **Token Refresh Endpoint**
```
POST https://api.codemurf.com/auth/refresh
Content-Type: application/json
Authorization: Bearer {refresh_token}
```

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response:**
```json
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "expires_in": 3600
}
```

---

### 4. **User Info Endpoint**
```
GET https://api.codemurf.com/auth/me
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "user-123",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "avatar_url": "https://...",
  "organization_id": "org-123",
  "permissions": ["read", "write", "admin"]
}
```

---

### 5. **Logout Endpoint**
```
POST https://api.codemurf.com/auth/logout
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

---

## 🧪 Testing Plan

### 1. **Local Development Testing**
```bash
# Set environment variables for local testing
export CODEMURF_API_URL="http://localhost:3000"
export CODEMURF_WEB_URL="http://localhost:4200"

# Run the extension
./dev.sh
# Press F5
```

### 2. **Test Scenarios**

#### Scenario 1: First-Time User Login
1. Open extension → Should show welcome/login page
2. Click "Sign In" → Opens browser to CodeMurf
3. Enter credentials → Authenticates
4. Redirects back → Shows success
5. Extension shows chat view

#### Scenario 2: Returning User
1. Open extension → Should go directly to chat
2. Check localStorage has `kilocode_authenticated = true`

#### Scenario 3: Invalid State (Security)
1. Manually trigger callback with wrong state
2. Should reject and show error

#### Scenario 4: Token Expiration
1. Wait for token to expire
2. Extension should auto-refresh
3. If refresh fails, should prompt re-login

#### Scenario 5: Logout
1. Click logout button
2. Clear authentication
3. Show welcome/login page again

---

## 📝 Translation Keys Needed

Add these to `/webview-ui/src/i18n/locales/en/welcome.json`:

```json
{
  "routers": {
    "codemurf": {
      "description": "Access 400+ AI models with CodeMurf Cloud",
      "incentive": "$20 bonus credits on first top-up"
    }
  },
  "auth": {
    "title": "Sign in to CodeMurf",
    "subtitle": "Sign in to access your account and continue",
    "signIn": {
      "title": "Sign In",
      "subtitle": "Welcome back to CodeMurf",
      "button": "Sign In",
      "link": "Sign in"
    },
    "signUp": {
      "title": "Create Account",
      "subtitle": "Join CodeMurf today",
      "button": "Create Account",
      "link": "Sign up"
    },
    "success": {
      "title": "Authentication Successful!",
      "message": "You're now signed in to CodeMurf"
    },
    "errors": {
      "unknownError": "An unknown error occurred"
    }
  }
}
```

---

## 🚀 Implementation Checklist

- [ ] Update `/packages/cloud/src/config.ts` with CodeMurf URLs
- [ ] Modify `/packages/cloud/src/WebAuthService.ts`:
  - [ ] Update `login()` method
  - [ ] Update `handleCallback()` method
  - [ ] Add `exchangeCodeForTokens()` method
  - [ ] Add token refresh logic
- [ ] Update `/webview-ui/src/oauth/urls.ts`
- [ ] Update `/webview-ui/src/components/welcome/WelcomeView.tsx`
- [ ] Add translation keys
- [ ] Add CodeMurf logo to `/webview-ui/public/`
- [ ] Backend: Implement authorization endpoint
- [ ] Backend: Implement token exchange endpoint
- [ ] Backend: Implement token refresh endpoint
- [ ] Backend: Implement user info endpoint
- [ ] Backend: Implement logout endpoint
- [ ] Test local development flow
- [ ] Test production flow
- [ ] Security audit
- [ ] Documentation update

---

## 📞 Next Steps

1. **Review this document** with your backend team
2. **Implement backend endpoints** as specified
3. **Update extension configuration** files
4. **Test authentication flow** locally
5. **Deploy and test** in staging environment

---

## 🔗 Related Files

- Extension Config: `/packages/cloud/src/config.ts`
- Auth Service: `/packages/cloud/src/WebAuthService.ts`
- OAuth URLs: `/webview-ui/src/oauth/urls.ts`
- Welcome View: `/webview-ui/src/components/welcome/WelcomeView.tsx`
- Auth Form: `/webview-ui/src/components/auth/AuthenticationForm.tsx`

---

**Need Help?** Contact the development team or refer to the existing Kilocode authentication implementation.
