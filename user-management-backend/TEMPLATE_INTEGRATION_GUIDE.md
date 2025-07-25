# 🚀 Template API - Ready for Website Integration

## ✅ WORKING API ENDPOINTS (Tested & Verified)

### 🌐 Base URL: `http://localhost:8000`

---

## 📋 **MAIN ENDPOINTS FOR WEBSITE**

### 1. 🔍 **GET All Templates** (Public - No Auth Required)
```
GET /templates
```
**Query Parameters:**
- `category`, `plan_type`, `difficulty_level`, `featured`, `search`, `page`, `limit`

**Example:**
```bash
curl -X GET "http://localhost:8000/templates?plan_type=Free&page=1&limit=12"
```

### 2. 🔍 **GET Single Template** (Public - No Auth Required)
```
GET /templates/{template_id}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/templates/687d332c8ee8ad7d3d2ee5b2"
```

### 3. 📂 **GET Categories** (Public - No Auth Required)
```
GET /templates/categories
```

### 4. 📊 **GET Statistics** (Public - No Auth Required)
```
GET /templates/stats
```

---

## 🔐 **USER ACTION ENDPOINTS** (Require Authentication)

### 5. ❤️ **Like/Unlike Template**
```
POST /templates/{template_id}/like
Headers: Authorization: Bearer {token}
```

### 6. 📥 **Download Template**
```
POST /templates/{template_id}/download
Headers: Authorization: Bearer {token}
```

### 7. 👤 **My Templates**
```
GET /templates/user/my-templates
Headers: Authorization: Bearer {token}
```

---

## 🔑 **AUTHENTICATION**

### Login to get token:
```bash
curl -X POST "http://localhost:8000/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser_20250720_234038@example.com", "password": "TestPassword123!"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## 📊 **TEMPLATE DATA STRUCTURE**

Each template contains:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Modern Portfolio Template",
  "category": "Portfolio",
  "type": "React",
  "language": "TypeScript", 
  "difficulty_level": "Easy",
  "plan_type": "Free",
  "pricing_inr": 0,
  "pricing_usd": 0,
  "rating": 4.5,
  "downloads": 1250,
  "views": 3500,
  "likes": 890,
  "short_description": "Brief description",
  "full_description": "Detailed description",
  "preview_images": ["image1.jpg", "image2.jpg"],
  "git_repo_url": "https://github.com/user/repo",
  "live_demo_url": "https://demo.example.com",
  "dependencies": ["react", "typescript"],
  "tags": ["portfolio", "modern"],
  "developer_name": "John Doe",
  "developer_experience": "5+ years",
  "featured": true,
  "popular": true,
  "code": "// Template source code",
  "readme_content": "# README",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user_id": "507f1f77bcf86cd799439012"
}
```

---

## 🎨 **JAVASCRIPT INTEGRATION EXAMPLES**

### Fetch Templates for Gallery:
```javascript
const fetchTemplates = async (page = 1, filters = {}) => {
  const params = new URLSearchParams({
    page: page,
    limit: 12,
    ...filters
  });
  
  const response = await fetch(`http://localhost:8000/templates?${params}`);
  const data = await response.json();
  return data;
};

// Usage
const templates = await fetchTemplates(1, { 
  plan_type: 'Free',
  category: 'Portfolio' 
});
```

### Search Templates:
```javascript
const searchTemplates = async (searchTerm) => {
  const response = await fetch(`http://localhost:8000/templates?search=${searchTerm}`);
  return response.json();
};
```

### Like Template:
```javascript
const likeTemplate = async (templateId, accessToken) => {
  const response = await fetch(`http://localhost:8000/templates/${templateId}/like`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return response.json();
};
```

### Download Template:
```javascript
const downloadTemplate = async (templateId, accessToken) => {
  const response = await fetch(`http://localhost:8000/templates/${templateId}/download`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return response.json();
};
```

---

## 🧪 **CURRENT TEST DATA**

**Available Templates:** 1 template currently in database
**Test User Credentials:**
- Email: `testuser_20250720_234038@example.com`
- Password: `TestPassword123!`

---

## 🔄 **API RESPONSE FORMAT**

All responses follow this structure:
```json
{
  "success": true,
  "templates": [...],
  "pagination": {
    "page": 1,
    "limit": 12,
    "total": 45,
    "pages": 4
  }
}
```

---

## ⚡ **QUICK START FOR FRONTEND**

1. **Display Templates:**
   ```javascript
   fetch('http://localhost:8000/templates')
     .then(res => res.json())
     .then(data => console.log(data.templates));
   ```

2. **Filter by Category:**
   ```javascript
   fetch('http://localhost:8000/templates?category=Portfolio&plan_type=Free')
     .then(res => res.json())
     .then(data => displayTemplates(data.templates));
   ```

3. **Get Template Details:**
   ```javascript
   fetch(`http://localhost:8000/templates/${templateId}`)
     .then(res => res.json())
     .then(data => showTemplateDetails(data.template));
   ```

---

## 🎯 **READY FOR INTEGRATION!**

✅ **All APIs tested and working**
✅ **Authentication system ready**  
✅ **Template data structure documented**
✅ **JavaScript examples provided**
✅ **Search and filtering available**
✅ **User actions (like/download) working**

**Your backend is ready for frontend integration!** 🚀
