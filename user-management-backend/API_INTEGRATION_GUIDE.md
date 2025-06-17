# VS Code Extension API Integration Guide

## 🚀 Base Configuration

```javascript
const API_CONFIG = {
  baseURL: "http://localhost:8000",  // Development
  // baseURL: "https://your-production-domain.com",  // Production
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json"
  }
};
```

## 🔐 Authentication Methods

### Method 1: JWT Token Authentication (Recommended for users)
```javascript
// Headers for JWT authentication
const authHeaders = {
  "Authorization": `Bearer ${accessToken}`,
  "Content-Type": "application/json"
};
```

### Method 2: API Key Authentication (Recommended for applications)
```javascript
// Headers for API key authentication
const apiKeyHeaders = {
  "X-API-Key": "${apiKey}",
  "Content-Type": "application/json"
};
```

## 📚 Complete API Endpoints Reference

### 1. Authentication Endpoints

#### Register User
```javascript
POST /auth/register
Content-Type: application/json

// Request Body
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

// Response (200)
{
  "id": 1,
  "email": "user@example.com",
  "subscription": "free",
  "created_at": "2025-06-08T10:30:00Z",
  "message": "User registered successfully"
}
```

#### Login User
```javascript
POST /auth/login
Content-Type: application/x-www-form-urlencoded

// Request Body (Form data)
username=user@example.com&password=SecurePassword123!

// Response (200)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Refresh Token
```javascript
POST /auth/refresh
Content-Type: application/json

// Request Body
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

// Response (200)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 2. User Management Endpoints

#### Get Current User
```javascript
GET /users/me
Authorization: Bearer ${accessToken}

// Response (200)
{
  "id": 1,
  "email": "user@example.com",
  "subscription": "free",
  "created_at": "2025-06-08T10:30:00Z",
  "tokens_used": 150,
  "tokens_limit": 1000,
  "api_calls_used": 25,
  "api_calls_limit": 100
}
```

#### Update User Profile
```javascript
PUT /users/me
Authorization: Bearer ${accessToken}
Content-Type: application/json

// Request Body
{
  "email": "newemail@example.com"
}

// Response (200)
{
  "id": 1,
  "email": "newemail@example.com",
  "subscription": "free",
  "created_at": "2025-06-08T10:30:00Z"
}
```

### 3. API Key Management

#### Create API Key
```javascript
POST /api/keys
Authorization: Bearer ${accessToken}
Content-Type: application/json

// Request Body
{
  "name": "VS Code Extension Key",
  "description": "API key for my VS Code extension"
}

// Response (200)
{
  "id": "api_key_123",
  "name": "VS Code Extension Key",
  "description": "API key for my VS Code extension",
  "api_key": "ak_1234567890abcdef...",
  "created_at": "2025-06-08T10:30:00Z",
  "last_used": null,
  "is_active": true
}
```

#### List API Keys
```javascript
GET /api/keys
Authorization: Bearer ${accessToken}

// Response (200)
[
  {
    "id": "api_key_123",
    "name": "VS Code Extension Key",
    "description": "API key for my VS Code extension",
    "created_at": "2025-06-08T10:30:00Z",
    "last_used": "2025-06-08T11:00:00Z",
    "is_active": true
  }
]
```

#### Revoke API Key
```javascript
DELETE /api/keys/{key_id}
Authorization: Bearer ${accessToken}

// Response (200)
{
  "message": "API key revoked successfully"
}
```

### 4. Subscription Management

#### Get Current Subscription
```javascript
GET /subscriptions/current
Authorization: Bearer ${accessToken}
// OR
X-API-Key: ${apiKey}

// Response (200)
{
  "subscription": "free",
  "tokens_used": 150,
  "tokens_limit": 1000,
  "api_calls_used": 25,
  "api_calls_limit": 100,
  "features": {
    "api_access": true,
    "premium_models": false,
    "priority_support": false,
    "advanced_analytics": false
  },
  "billing_cycle": "monthly",
  "next_billing_date": null
}
```

#### List Subscription Plans
```javascript
GET /subscriptions/plans

// Response (200)
[
  {
    "name": "free",
    "display_name": "Free Plan",
    "price": 0,
    "tokens_limit": 1000,
    "api_calls_limit": 100,
    "features": {
      "api_access": true,
      "premium_models": false,
      "priority_support": false,
      "advanced_analytics": false
    }
  },
  {
    "name": "pro",
    "display_name": "Pro Plan",
    "price": 10.00,
    "tokens_limit": 10000,
    "api_calls_limit": 1000,
    "features": {
      "api_access": true,
      "premium_models": true,
      "priority_support": true,
      "advanced_analytics": true
    }
  }
]
```

#### Get Usage Statistics
```javascript
GET /subscriptions/usage
Authorization: Bearer ${accessToken}
// OR
X-API-Key: ${apiKey}

// Response (200)
{
  "current_period": {
    "start_date": "2025-06-01T00:00:00Z",
    "end_date": "2025-06-30T23:59:59Z",
    "tokens_used": 150,
    "tokens_limit": 1000,
    "api_calls_used": 25,
    "api_calls_limit": 100
  },
  "daily_usage": [
    {
      "date": "2025-06-08",
      "tokens_used": 50,
      "api_calls_used": 10
    }
  ]
}
```

### 5. LLM Service Endpoints

#### LLM Health Check
```javascript
GET /llm/health
Authorization: Bearer ${accessToken}
// OR
X-API-Key: ${apiKey}

// Response (200)
{
  "status": "healthy",
  "providers": ["openai", "anthropic", "gemini"],
  "total_models": 15
}
```

#### List LLM Providers
```javascript
GET /llm/providers
Authorization: Bearer ${accessToken}
// OR
X-API-Key: ${apiKey}

// Response (200)
[
  {
    "id": "openai",
    "name": "OpenAI",
    "status": "active",
    "models_count": 8
  },
  {
    "id": "anthropic",
    "name": "Anthropic",
    "status": "active",
    "models_count": 4
  },
  {
    "id": "gemini",
    "name": "Google Gemini",
    "status": "active",
    "models_count": 3
  }
]
```

#### List LLM Models
```javascript
GET /llm/models
Authorization: Bearer ${accessToken}
// OR
X-API-Key: ${apiKey}

// Query Parameters
?provider=openai&tier=pro

// Response (200)
[
  {
    "id": "gpt-4",
    "name": "GPT-4",
    "provider": "openai",
    "tier": "pro",
    "description": "Most capable GPT-4 model",
    "max_tokens": 8192,
    "cost_per_token": 0.00003
  },
  {
    "id": "gpt-3.5-turbo",
    "name": "GPT-3.5 Turbo",
    "provider": "openai", 
    "tier": "free",
    "description": "Fast and efficient model",
    "max_tokens": 4096,
    "cost_per_token": 0.000002
  }
]
```

### 6. Health Check Endpoints

#### System Health
```javascript
GET /health

// Response (200)
{
  "status": "healthy",
  "app": "User Management Backend"
}
```

#### Root Endpoint
```javascript
GET /

// Response (200)
{
  "message": "User Management Backend API",
  "status": "healthy"
}
```

## 📊 Rate Limiting Headers

All API responses include rate limiting headers:

```javascript
// Response Headers
{
  "X-RateLimit-Limit": "100",        // Requests per hour limit
  "X-RateLimit-Remaining": "95",     // Remaining requests
  "X-RateLimit-Reset": "1749333600", // Reset time (Unix timestamp)
  "X-RateLimit-Tier": "free",        // User's subscription tier
  "X-Process-Time": "0.123"          // Request processing time
}
```

## 🎯 Rate Limits by Tier

```javascript
const RATE_LIMITS = {
  free: {
    general: 100,    // requests per hour
    llm: 50,         // LLM requests per hour
    auth: 20         // Auth requests per hour
  },
  pro: {
    general: 1000,
    llm: 500,
    auth: 100
  },
  enterprise: {
    general: 10000,
    llm: 5000,
    auth: 500
  },
  api_key: {
    general: 2000,
    llm: 1000,
    auth: 200
  }
};
```

## 🔧 VS Code Extension Integration Examples

### 1. Authentication Flow
```javascript
class APIClient {
  constructor() {
    this.baseURL = "http://localhost:8000";
    this.accessToken = null;
    this.refreshToken = null;
    this.apiKey = null;
  }

  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString()
    });

    if (response.ok) {
      const data = await response.json();
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      return data;
    }
    throw new Error('Login failed');
  }

  async createAPIKey(name, description) {
    const response = await fetch(`${this.baseURL}/api/keys`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name, description })
    });

    if (response.ok) {
      const data = await response.json();
      this.apiKey = data.api_key;
      return data;
    }
    throw new Error('API key creation failed');
  }

  async makeAuthenticatedRequest(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.apiKey 
        ? { 'X-API-Key': this.apiKey }
        : { 'Authorization': `Bearer ${this.accessToken}` }
      ),
      ...options.headers
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers
    });

    // Handle rate limiting
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      throw new Error(`Rate limited. Retry after ${retryAfter} seconds`);
    }

    // Handle token expiration
    if (response.status === 401 && this.refreshToken) {
      await this.refreshAccessToken();
      return this.makeAuthenticatedRequest(endpoint, options);
    }

    return response;
  }

  async refreshAccessToken() {
    const response = await fetch(`${this.baseURL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: this.refreshToken })
    });

    if (response.ok) {
      const data = await response.json();
      this.accessToken = data.access_token;
      return data;
    }
    throw new Error('Token refresh failed');
  }

  async getUserInfo() {
    const response = await this.makeAuthenticatedRequest('/users/me');
    return response.json();
  }

  async getSubscriptionInfo() {
    const response = await this.makeAuthenticatedRequest('/subscriptions/current');
    return response.json();
  }

  async getLLMModels(provider = null) {
    const query = provider ? `?provider=${provider}` : '';
    const response = await this.makeAuthenticatedRequest(`/llm/models${query}`);
    return response.json();
  }
}
```

### 2. Usage in VS Code Extension
```javascript
// In your VS Code extension
const vscode = require('vscode');

let apiClient = new APIClient();

async function activate(context) {
  // Register commands
  let loginCommand = vscode.commands.registerCommand('extension.login', async () => {
    const email = await vscode.window.showInputBox({ prompt: 'Enter email' });
    const password = await vscode.window.showInputBox({ 
      prompt: 'Enter password', 
      password: true 
    });

    try {
      await apiClient.login(email, password);
      vscode.window.showInformationMessage('Login successful!');
      
      // Create API key for persistent authentication
      const keyData = await apiClient.createAPIKey(
        'VS Code Extension',
        'Persistent API key for VS Code extension'
      );
      
      // Store API key securely
      await context.secrets.store('api_key', keyData.api_key);
      
    } catch (error) {
      vscode.window.showErrorMessage(`Login failed: ${error.message}`);
    }
  });

  let checkUsageCommand = vscode.commands.registerCommand('extension.checkUsage', async () => {
    try {
      const usage = await apiClient.getSubscriptionInfo();
      const message = `Usage: ${usage.tokens_used}/${usage.tokens_limit} tokens, ${usage.api_calls_used}/${usage.api_calls_limit} API calls`;
      vscode.window.showInformationMessage(message);
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to get usage: ${error.message}`);
    }
  });

  context.subscriptions.push(loginCommand, checkUsageCommand);

  // Load stored API key
  const storedApiKey = await context.secrets.get('api_key');
  if (storedApiKey) {
    apiClient.apiKey = storedApiKey;
  }
}
```

## ⚠️ Error Handling

### Common Error Responses
```javascript
// 400 Bad Request
{
  "detail": "Invalid request data"
}

// 401 Unauthorized
{
  "detail": "Could not validate credentials"
}

// 403 Forbidden
{
  "detail": "Not authenticated"
}

// 404 Not Found
{
  "detail": "Not Found"
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}

// 429 Rate Limited
{
  "detail": {
    "error": "rate_limit_exceeded",
    "message": "Rate limit exceeded for general endpoints",
    "rate_limit": {
      "limit": 100,
      "remaining": 0,
      "reset": 1749333600,
      "tier": "free"
    }
  }
}
```

## 🔄 Best Practices for VS Code Extension

1. **Use API Keys for persistent authentication** instead of JWT tokens
2. **Store API keys securely** using VS Code's secrets API
3. **Handle rate limiting gracefully** with exponential backoff
4. **Cache user info and subscription data** to reduce API calls
5. **Show usage statistics** to users to help them manage their limits
6. **Implement proper error handling** with user-friendly messages
7. **Use the health endpoints** to check API availability before making requests

## 📋 Environment Configuration

```javascript
// Development
const DEV_CONFIG = {
  baseURL: "http://localhost:8000",
  timeout: 30000
};

// Production
const PROD_CONFIG = {
  baseURL: "https://your-production-domain.com",
  timeout: 30000
};

const config = process.env.NODE_ENV === 'production' ? PROD_CONFIG : DEV_CONFIG;
```

This comprehensive guide provides everything needed to integrate your VS Code extension with the backend marketplace API, including authentication, data structures, error handling, and best practices.
