# 🚀 AIML API Integration Guide

## ✅ **AIML Support Status: FULLY IMPLEMENTED**

Your backend marketplace system now has **complete AIML API support** integrated alongside your existing providers (OpenRouter, Glama, Requesty).

## 🔧 **Configuration Required**

### Environment Variables (.env file)
Add these to your `.env` file:

```bash
# AIML API Configuration
AIML_API_KEY=your_actual_aiml_api_key_here
AIML_CLIENT_ID=your_aiml_oauth_client_id
AIML_CLIENT_SECRET=your_aiml_oauth_client_secret
```

### Obtaining AIML Credentials
1. **API Key**: Visit [AIML API Console](https://api.aimlapi.com) to get your API key
2. **OAuth Credentials**: Register your application for OAuth integration (if needed)

## 🎯 **How to Use AIML in Your VS Code Extension**

### 1. **API Key Authentication**
```javascript
// Use AIML with API key authentication
const response = await fetch(`${API_BASE_URL}/llm/chat/completions`, {
  method: 'POST',
  headers: {
    'X-API-Key': 'your_marketplace_api_key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'aiml/gpt-4',  // Use aiml/ prefix for AIML models
    messages: [
      { role: 'user', content: 'Hello from VS Code!' }
    ]
  })
});
```

### 2. **OAuth Authentication**
```javascript
// AIML OAuth login endpoint
const aimlLoginUrl = `${API_BASE_URL}/auth/aiml/login`;

// Redirect user to AIML OAuth
window.open(aimlLoginUrl, '_blank');
```

### 3. **Model Selection**
Use these prefixes to route to AIML:
- `aiml/model-name` - Routes to AIML
- `aiml/gpt-4` - AIML GPT-4
- `aiml/claude-3` - AIML Claude-3

## 📚 **Available Endpoints with AIML Support**

### Chat Completions
```bash
POST /llm/chat/completions
{
  "model": "aiml/gpt-4",
  "messages": [...]
}
```

### Text Completions
```bash
POST /llm/completions
{
  "model": "aiml/gpt-3.5-turbo",
  "prompt": "Complete this text..."
}
```

### Embeddings
```bash
POST /llm/embeddings
{
  "model": "aiml/text-embedding-ada-002",
  "input": "Text to embed"
}
```

### List Models
```bash
GET /llm/models
# Returns models from all providers including AIML
```

### List Providers
```bash
GET /llm/providers
# Returns: ["openrouter", "glama", "requesty", "aiml"]
```

## 🔐 **Authentication Options**

### Option 1: API Key (Recommended for VS Code Extension)
```javascript
headers: {
  'X-API-Key': 'sk_live_your_marketplace_api_key'
}
```

### Option 2: JWT Token
```javascript
headers: {
  'Authorization': 'Bearer your_jwt_token'
}
```

### Option 3: OAuth (for web interfaces)
```javascript
// Redirect to AIML OAuth
GET /auth/aiml/login
```

## 🔑 **How Users Obtain API Keys for AIML Access**

### API Key System Architecture

The API key system involves two separate types of keys:

1. **Backend Admin Setup**: As the backend administrator, you need to:
   - Obtain an AIML API key from [AIML API Console](https://api.aimlapi.com)
   - Add this key to your backend's `.env` file as `AIML_API_KEY`

2. **VS Code Extension User Setup**: Your extension users need to:
   - Create an API key from YOUR marketplace backend
   - Store this key in their VS Code extension
   - Use this key to make requests to your backend

**Important**: Users of your VS Code extension never interact directly with AIML's API. 
Instead, they authenticate with your backend, which proxies their requests 
to AIML using your administrator-level AIML API key.

### Creating a Marketplace API Key (For Extension Users)

Here's the flow your users will follow:

```javascript
// Step 1: Authenticate with marketplace backend
const authResponse = await fetch("http://localhost:8000/auth/login", {
  method: "POST",
  // Authentication details
});
const token = (await authResponse.json()).access_token;

// Step 2: Create an API key
const keyResponse = await fetch("http://localhost:8000/api/keys", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    name: "VS Code Extension Key",
    description: "For VS Code extension use"
  })
});

// Step 3: Store the key securely
const keyData = await keyResponse.json();
await context.secrets.store("marketplace_api_key", keyData.api_key);
```

This marketplace API key is what end-users will use to authenticate all their requests
to your backend, including those that access AIML services.

### Full User Onboarding Flow

1. User installs your VS Code extension
2. User logs in with their credentials (OAuth or username/password)
3. Extension creates a marketplace API key for the user
4. Extension stores this API key securely using VS Code's SecretStorage API
5. User makes LLM requests through your backend using this API key
6. Your backend proxies these requests to AIML using YOUR administrator AIML API key
7. Responses return to the user via your backend

## 🎛️ **Model Routing Logic**

The system automatically routes requests based on model names:

```javascript
// These all route to AIML:
"aiml/gpt-4"           → AIML Provider
"aiml/claude-3"        → AIML Provider
"aiml/text-ada-002"    → AIML Provider

// Other providers:
"openrouter/gpt-4"     → OpenRouter
"glama/llama-2"        → Glama  
"requesty/claude-2"    → Requesty
"gpt-4"                → OpenRouter (default)
```

## 💡 **VS Code Extension Integration Example**

### Complete Integration Code
```javascript
class AIMLIntegration {
  constructor(apiKey, baseURL = 'http://localhost:8000') {
    this.apiKey = apiKey;
    this.baseURL = baseURL;
  }

  async chatWithAIML(messages, model = 'aiml/gpt-4') {
    try {
      const response = await fetch(`${this.baseURL}/llm/chat/completions`, {
        method: 'POST',
        headers: {
          'X-API-Key': this.apiKey,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: model,
          messages: messages,
          max_tokens: 1000,
          temperature: 0.7
        })
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }

      const data = await response.json();
      
      // Check for usage info
      if (data._usage_info) {
        console.log('Tokens used:', data._usage_info.tokens_used);
        console.log('Cost:', data._usage_info.cost_usd);
        console.log('Remaining tokens:', data._usage_info.remaining_tokens);
      }

      return data;
    } catch (error) {
      console.error('AIML API Error:', error);
      throw error;
    }
  }

  async getAIMLModels() {
    const response = await fetch(`${this.baseURL}/llm/models?provider=aiml`, {
      headers: { 'X-API-Key': this.apiKey }
    });
    return response.json();
  }

  async checkAIMLStatus() {
    const response = await fetch(`${this.baseURL}/llm/providers`, {
      headers: { 'X-API-Key': this.apiKey }
    });
    const data = await response.json();
    return data.find(p => p.id === 'aiml')?.status === 'active';
  }
}

// Usage in VS Code extension
const aiml = new AIMLIntegration(storedApiKey);

// Check if AIML is available
if (await aiml.checkAIMLStatus()) {
  // Use AIML for chat
  const response = await aiml.chatWithAIML([
    { role: 'user', content: 'Help me write better code' }
  ]);
  
  console.log('AIML Response:', response.choices[0].message.content);
}
```

## 🧪 **Testing AIML Integration**

### Run Integration Tests
```powershell
# Test AIML configuration
python -c "from app.config import settings; print('AIML configured:', hasattr(settings, 'aiml_api_key'))"

# Test AIML client
python -c "from app.services.llm_proxy_service import AIMLClient; client = AIMLClient(); print('AIML Client URL:', client.base_url)"

# Test provider integration
python -c "from app.services.llm_proxy_service import LLMProxyService; from app.database import SessionLocal; db = SessionLocal(); proxy = LLMProxyService(db); print('Providers:', list(proxy.providers.keys())); db.close()"

# Run comprehensive test
python test_aiml_integration.py
```

### Expected Test Output
```
✅ Config imported successfully
AIML config attributes: ['aiml_api_key', 'aiml_client_id', 'aiml_client_secret']
✅ AIML Client imported successfully
✅ AIML Client created with base URL: https://api.aimlapi.com/v1
✅ LLM Proxy Service created with providers: ['openrouter', 'glama', 'requesty', 'aiml']
✅ Model routing works: aiml/gpt-4 -> aiml
🎉 All AIML integration tests passed!
```

## 🚨 **Rate Limiting & Token Management**

AIML requests are subject to the same token management as other providers:

- **Free Tier**: 10,000 tokens/month
- **Pro Tier**: 100,000 tokens/month  
- **Enterprise**: 1,000,000 tokens/month

### Usage Tracking
Every AIML request automatically:
1. ✅ Reserves tokens before the call
2. ✅ Logs actual usage after completion
3. ✅ Updates user's remaining balance
4. ✅ Enforces plan limits

## 📊 **Monitoring & Analytics**

### Usage Statistics
```javascript
// Get usage info for AIML specifically
GET /subscriptions/usage?provider=aiml

// Response includes:
{
  "provider": "aiml",
  "tokens_used": 1250,
  "requests_count": 15,
  "cost_total": 0.03,
  "average_tokens_per_request": 83
}
```

## 🎯 **Next Steps**

1. **Add your AIML API key** to the `.env` file
2. **Test with real API calls** using the examples above
3. **Update your VS Code extension** to use AIML models
4. **Monitor usage** through the analytics endpoints
5. **Configure AIML OAuth** if needed for user authentication

## 🔧 **Troubleshooting**

### Common Issues

**"AIML provider not found"**
- Check that AIML is in your OAuth providers list: `python -c "from app.config import settings; print(settings.oauth_providers)"`

**"Invalid API key"**
- Verify your AIML API key is correct in the `.env` file
- Test the key directly with AIML's API

**"Model routing fails"**
- Use the `aiml/` prefix: `aiml/gpt-4`, not just `gpt-4`
- Check provider routing: `python -c "from app.services.llm_proxy_service import LLMProxyService; from app.database import SessionLocal; db = SessionLocal(); proxy = LLMProxyService(db); print(proxy.get_provider_from_model('aiml/gpt-4')); db.close()"`

**"Token limits exceeded"**
- Check user's subscription and token balance
- Upgrade plan if needed

---

## ✅ **Summary**

🎉 **AIML is now fully integrated** into your backend marketplace system! 

**What's Working:**
- ✅ AIML client implementation
- ✅ OAuth configuration  
- ✅ API key authentication
- ✅ Model routing (`aiml/model-name`)
- ✅ Token management & rate limiting
- ✅ Usage tracking & analytics
- ✅ All API endpoints support AIML

**Ready to Use:**
- Chat completions: `POST /llm/chat/completions`
- Text completions: `POST /llm/completions`  
- Embeddings: `POST /llm/embeddings`
- Model listing: `GET /llm/models`
- Provider status: `GET /llm/providers`

Your VS Code extension can now seamlessly use AIML alongside OpenRouter, Glama, and Requesty! 🚀
