 # 📋 Template API Documentation for Website Integration

## 🚀 Base URL
```
http://localhost:8000
```

## 🔐 Authentication
All protected endpoints require Bearer token authentication:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Login to get token:**
```bash
curl -X POST "http://localhost:8000/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser_20250720_234038@example.com", "password": "TestPassword123!"}'
```

---

## 📋 Template API Endpoints

### 1. 🔍 GET All Templates (Public)
**Endpoint:** `GET /templates`

**Description:** Get all templates with filtering, searching, and pagination

**Query Parameters:**
- `category` (optional): Filter by category (e.g., "Portfolio", "E-commerce")
- `plan_type` (optional): Filter by plan type ("Free" or "Paid")
- `difficulty_level` (optional): Filter by difficulty ("Easy", "Medium", "Tough")
- `featured` (optional): Filter featured templates (true/false)
- `search` (optional): Search in title, description, and tags
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/templates?category=Portfolio&plan_type=Free&page=1&limit=10"
```

**Example Response:**
```json
{
  "success": true,
  "templates": [
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
      "short_description": "A modern, responsive portfolio template",
      "full_description": "Complete description...",
      "preview_images": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg"
      ],
      "git_repo_url": "https://github.com/user/repo",
      "live_demo_url": "https://demo.example.com",
      "dependencies": ["react", "typescript", "tailwindcss"],
      "tags": ["portfolio", "modern", "responsive"],
      "developer_name": "John Doe",
      "developer_experience": "5+ years",
      "is_available_for_dev": true,
      "featured": true,
      "popular": true,
      "code": "// Template code here",
      "readme_content": "# Template README",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "is_active": true,
      "user_id": "507f1f77bcf86cd799439012"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "pages": 5
  }
}
```

---

### 2. 🔍 GET Single Template (Public)
**Endpoint:** `GET /templates/{template_id}`

**Description:** Get a specific template by ID (increments view count)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/templates/507f1f77bcf86cd799439011"
```

**Example Response:**
```json
{
  "success": true,
  "template": {
    "id": "507f1f77bcf86cd799439011",
    "title": "Modern Portfolio Template",
    // ... full template object (same as above)
  }
}
```

---

### 3. 📊 GET Template Categories (Public)
**Endpoint:** `GET /templates/categories`

**Description:** Get all available template categories

**Example Request:**
```bash
curl -X GET "http://localhost:8000/templates/categories"
```

**Example Response:**
```json
{
  "success": true,
  "categories": [
    "Admin Panel",
    "Blog",
    "Dashboard",
    "E-commerce",
    "Landing Page",
    "Learning Management System",
    "Portfolio",
    "SaaS Tool"
  ]
}
```

---

### 4. 📈 GET Template Statistics (Public)
**Endpoint:** `GET /templates/stats`

**Description:** Get template statistics overview

**Example Request:**
```bash
curl -X GET "http://localhost:8000/templates/stats"
```

**Example Response:**
```json
{
  "success": true,
  "stats": {
    "total_templates": 150,
    "free_templates": 120,
    "paid_templates": 30,
    "featured_templates": 25,
    "categories_count": 8,
    "categories": [
      "Admin Panel",
      "Blog",
      "Dashboard",
      "E-commerce",
      "Landing Page",
      "Learning Management System", 
      "Portfolio",
      "SaaS Tool"
    ]
  }
}
```

---

### 5. ❤️ POST Like/Unlike Template (Protected)
**Endpoint:** `POST /templates/{template_id}/like`

**Description:** Like or unlike a template (toggles)

**Authentication:** Required

**Example Request:**
```bash
curl -X POST "http://localhost:8000/templates/507f1f77bcf86cd799439011/like" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Response:**
```json
{
  "success": true,
  "liked": true,
  "likes_count": 891,
  "message": "Template liked successfully"
}
```

---

### 6. 📥 POST Download Template (Protected)
**Endpoint:** `POST /templates/{template_id}/download`

**Description:** Record a template download (increments download count)

**Authentication:** Required

**Example Request:**
```bash
curl -X POST "http://localhost:8000/templates/507f1f77bcf86cd799439011/download" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Response:**
```json
{
  "success": true,
  "template": {
    "id": "507f1f77bcf86cd799439011",
    "downloads": 1251,
    // ... full template object
  },
  "message": "Download recorded successfully"
}
```

---

### 7. 👤 GET My Templates (Protected)
**Endpoint:** `GET /templates/user/my-templates`

**Description:** Get templates created by the current user

**Authentication:** Required

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/templates/user/my-templates?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 8. ➕ POST Create Template (Protected)
**Endpoint:** `POST /templates`

**Description:** Create a new template

**Authentication:** Required

**Request Body:**
```json
{
  "title": "My Awesome Template",
  "category": "Portfolio",
  "type": "React",
  "language": "TypeScript",
  "difficulty_level": "Medium",
  "plan_type": "Free",
  "pricing_inr": 0,
  "pricing_usd": 0,
  "short_description": "A brief description",
  "full_description": "Detailed description...",
  "preview_images": ["image1.jpg", "image2.jpg"],
  "git_repo_url": "https://github.com/user/repo",
  "live_demo_url": "https://demo.example.com",
  "dependencies": ["react", "typescript"],
  "tags": ["portfolio", "modern"],
  "developer_name": "John Doe",
  "developer_experience": "5+ years",
  "is_available_for_dev": true,
  "featured": false,
  "code": "// Template code",
  "readme_content": "# README"
}
```

---

### 9. ✏️ PUT Update Template (Protected)
**Endpoint:** `PUT /templates/{template_id}`

**Description:** Update an existing template (only owner can update)

**Authentication:** Required

---

### 10. 🗑️ DELETE Template (Protected)
**Endpoint:** `DELETE /templates/{template_id}`

**Description:** Delete a template (soft delete - sets is_active to false)

**Authentication:** Required

---

## 🏷️ Template Data Structure

### Template Object Fields:
- **id**: String - Unique template identifier
- **title**: String - Template title
- **category**: String - Template category
- **type**: String - Technology type (React, Vue, Angular, etc.)
- **language**: String - Programming language
- **difficulty_level**: String - "Easy", "Medium", or "Tough"
- **plan_type**: String - "Free" or "Paid"
- **pricing_inr**: Number - Price in Indian Rupees
- **pricing_usd**: Number - Price in US Dollars
- **rating**: Number - Average rating (0-5)
- **downloads**: Number - Download count
- **views**: Number - View count
- **likes**: Number - Like count
- **short_description**: String - Brief description
- **full_description**: String - Detailed description
- **preview_images**: Array - Image URLs
- **git_repo_url**: String - GitHub repository URL
- **live_demo_url**: String - Live demo URL
- **dependencies**: Array - Required dependencies
- **tags**: Array - Template tags
- **developer_name**: String - Creator name
- **developer_experience**: String - Developer experience
- **is_available_for_dev**: Boolean - Available for development
- **featured**: Boolean - Featured template
- **popular**: Boolean - Popular template
- **code**: String - Template source code
- **readme_content**: String - README content
- **created_at**: String - Creation timestamp (ISO format)
- **updated_at**: String - Last update timestamp (ISO format)
- **is_active**: Boolean - Template status
- **user_id**: String - Creator user ID

---

## 🎨 Website Integration Examples

### 1. Template Gallery Page
```javascript
// Fetch templates with filters
const fetchTemplates = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`http://localhost:8000/templates?${params}`);
  const data = await response.json();
  return data;
};

// Usage
const templates = await fetchTemplates({
  category: 'Portfolio',
  plan_type: 'Free',
  page: 1,
  limit: 12
});
```

### 2. Template Detail Page
```javascript
// Fetch single template
const fetchTemplate = async (templateId) => {
  const response = await fetch(`http://localhost:8000/templates/${templateId}`);
  const data = await response.json();
  return data.template;
};

// Record download
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

### 3. Like/Unlike Functionality
```javascript
const toggleLike = async (templateId, accessToken) => {
  const response = await fetch(`http://localhost:8000/templates/${templateId}/like`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return response.json();
};
```

### 4. Search and Filter
```javascript
const searchTemplates = async (searchTerm, filters = {}) => {
  const params = new URLSearchParams({
    search: searchTerm,
    ...filters
  });
  
  const response = await fetch(`http://localhost:8000/templates?${params}`);
  return response.json();
};
```

---

## 🚨 Error Handling

### Common Error Responses:
```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes:
- **200**: Success
- **400**: Bad Request (Invalid data)
- **401**: Unauthorized (Invalid/missing token)
- **403**: Forbidden (No permission)
- **404**: Not Found (Template doesn't exist)
- **500**: Internal Server Error

---

## 🔧 Testing the API

### Test with working credentials:
```bash
# 1. Login to get token
curl -X POST "http://localhost:8000/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser_20250720_234038@example.com", "password": "TestPassword123!"}'

# 2. Use the returned access_token for protected endpoints
curl -X GET "http://localhost:8000/templates" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

This comprehensive API documentation provides everything you need to integrate the template system into your website! 🚀
