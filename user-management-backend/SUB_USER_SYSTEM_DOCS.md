# Sub-User Management System Documentation

## Overview

The Sub-User Management System provides hierarchical user management capabilities, allowing main users to create and manage sub-users (subscreens) with granular permissions and resource limits.

## Key Features

### 🔐 Hierarchical Authentication
- Parent-child user relationships
- Independent API keys for sub-users
- Inherited subscription benefits
- Centralized billing through parent user

### 🎛️ Granular Permissions
- API access control
- Endpoint restrictions
- Model access limitations
- Settings modification permissions

### 📊 Resource Management
- Token limit allocation
- Rate limiting per sub-user
- API key quotas
- Usage tracking and analytics

### 📈 Scalability Features
- Subscription-based sub-user limits
- Bulk operations support
- Real-time monitoring
- Performance optimization

## API Endpoints

### Sub-User Management

#### Create Sub-User
```http
POST /sub-users/
Authorization: Bearer <parent_user_token>
Content-Type: application/json

{
  "email": "subuser@example.com",
  "name": "Sub User Name",
  "permissions": {
    "api_access": true,
    "can_create_api_keys": true,
    "can_view_usage": true,
    "can_modify_settings": false,
    "allowed_endpoints": ["*"],
    "allowed_models": ["gpt-3.5-turbo", "gpt-4"]
  },
  "limits": {
    "monthly_tokens": 5000,
    "requests_per_minute": 60,
    "max_api_keys": 3
  },
  "password": "secure_password123"
}
```

#### List Sub-Users
```http
GET /sub-users/
Authorization: Bearer <parent_user_token>
```

#### Update Sub-User Permissions
```http
PUT /sub-users/{sub_user_id}/permissions
Authorization: Bearer <parent_user_token>
Content-Type: application/json

{
  "permissions": {
    "api_access": true,
    "allowed_endpoints": ["/llm/chat/completions", "/llm/models"]
  }
}
```

#### Update Sub-User Limits
```http
PUT /sub-users/{sub_user_id}/limits
Authorization: Bearer <parent_user_token>
Content-Type: application/json

{
  "limits": {
    "monthly_tokens": 10000,
    "requests_per_minute": 100
  }
}
```

### API Key Management

#### Create Sub-User API Key
```http
POST /sub-users/{sub_user_id}/api-keys
Authorization: Bearer <parent_user_token>
Content-Type: application/json

{
  "name": "Production API Key",
  "description": "Key for production environment"
}
```

### Analytics & Monitoring

#### Get Sub-User Usage
```http
GET /sub-users/{sub_user_id}/usage
Authorization: Bearer <parent_user_token>
```

#### Dashboard Overview
```http
GET /dashboard/sub-users/overview
Authorization: Bearer <parent_user_token>
```

#### Usage Trends
```http
GET /dashboard/sub-users/usage-trends?days=30
Authorization: Bearer <parent_user_token>
```

## Permission System

### Available Permissions

| Permission | Description |
|------------|-------------|
| `api_access` | Basic API access |
| `can_create_api_keys` | Ability to create API keys |
| `can_view_usage` | Access to usage statistics |
| `can_modify_settings` | Modify own settings |
| `allowed_endpoints` | List of allowed API endpoints |
| `allowed_models` | List of allowed AI models |

### Default Permissions
```json
{
  "api_access": true,
  "can_create_api_keys": true,
  "can_view_usage": true,
  "can_modify_settings": false,
  "allowed_endpoints": ["*"],
  "allowed_models": ["*"]
}
```

## Resource Limits

### Configurable Limits

| Limit | Description | Default |
|-------|-------------|---------|
| `monthly_tokens` | Monthly token allocation | 5000 |
| `requests_per_minute` | Rate limit per minute | 60 |
| `requests_per_hour` | Rate limit per hour | 1000 |
| `max_api_keys` | Maximum API keys | 3 |
| `max_concurrent_requests` | Concurrent request limit | 10 |

### Subscription-Based Limits

| Subscription | Max Sub-Users | Features |
|-------------|---------------|----------|
| Free | 0 | No sub-users |
| Pro | 5 | Basic sub-user management |
| Enterprise | 50 | Advanced features, bulk operations |

## Usage Tracking

### Token Consumption
- Dual tracking: sub-user and parent user
- Separate limits enforcement
- Billing through parent account
- Real-time usage monitoring

### Analytics Data
- Daily/monthly usage trends
- Model-specific consumption
- Request patterns
- Performance metrics

## Implementation Architecture

### Database Schema
```sql
-- Sub-user fields added to users table
ALTER TABLE users ADD COLUMN parent_user_id TEXT;
ALTER TABLE users ADD COLUMN is_sub_user BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN sub_user_permissions TEXT; -- JSON
ALTER TABLE users ADD COLUMN sub_user_limits TEXT; -- JSON
```

### Key Components

1. **SubUserService** - Business logic for sub-user management
2. **Enhanced TokenService** - Token consumption with sub-user support
3. **Updated RateLimiter** - Sub-user specific rate limiting
4. **API Key Authentication** - Enhanced for sub-user keys
5. **Dashboard APIs** - Analytics and monitoring endpoints

## Scalability Considerations

### Performance Optimizations
- Indexed database queries
- Cached permission checks
- Efficient token tracking
- Background analytics processing

### Horizontal Scaling
- Stateless service design
- Redis-based rate limiting
- Distributed token tracking
- Load balancer friendly

### Resource Management
- Automatic limit enforcement
- Usage alerting
- Capacity planning tools
- Cost optimization features

## Security Features

### Authentication & Authorization
- Secure API key generation
- Permission validation
- Parent user verification
- Token-based authentication

### Data Protection
- Encrypted sensitive data
- Audit trail logging
- Access control enforcement
- Rate limiting protection

## Error Handling

### Common Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 400 | `INVALID_LIMITS` | Token limits exceed parent limits |
| 403 | `INSUFFICIENT_PERMISSIONS` | Sub-user lacks required permissions |
| 403 | `SUBSCRIPTION_REQUIRED` | Pro+ subscription required |
| 404 | `SUB_USER_NOT_FOUND` | Sub-user doesn't exist or access denied |
| 429 | `RATE_LIMIT_EXCEEDED` | Request rate limit exceeded |
| 429 | `TOKEN_LIMIT_EXCEEDED` | Monthly token limit exceeded |

## Integration Examples

### Creating a Sub-User with Custom Permissions
```python
import requests

# Create sub-user for API-only access
sub_user_data = {
    "email": "api-user@company.com",
    "name": "API Service Account",
    "permissions": {
        "api_access": True,
        "can_create_api_keys": True,
        "can_view_usage": False,
        "can_modify_settings": False,
        "allowed_endpoints": ["/llm/chat/completions"],
        "allowed_models": ["gpt-3.5-turbo"]
    },
    "limits": {
        "monthly_tokens": 50000,
        "requests_per_minute": 120,
        "max_api_keys": 1
    }
}

response = requests.post(
    "http://localhost:8000/sub-users/",
    json=sub_user_data,
    headers={"Authorization": f"Bearer {parent_token}"}
)
```

### Monitoring Sub-User Usage
```python
# Get usage trends
response = requests.get(
    "http://localhost:8000/dashboard/sub-users/usage-trends?days=30",
    headers={"Authorization": f"Bearer {parent_token}"}
)

trends = response.json()
print(f"Total tokens used: {trends['summary']['total_tokens']}")
print(f"Peak usage day: {trends['summary']['peak_day']}")
```

## Best Practices

1. **Permission Design**
   - Follow principle of least privilege
   - Use specific endpoint restrictions
   - Regular permission audits

2. **Resource Allocation**
   - Monitor usage patterns
   - Adjust limits based on needs
   - Plan for growth

3. **Security**
   - Rotate API keys regularly
   - Monitor unusual usage patterns
   - Implement usage alerts

4. **Monitoring**
   - Set up usage dashboards
   - Configure limit alerts
   - Track performance metrics

## Future Enhancements

- [ ] Role-based permission templates
- [ ] Advanced analytics and reporting
- [ ] Sub-user invitation system
- [ ] Bulk operations for enterprise users
- [ ] Integration with external identity providers
- [ ] Advanced rate limiting strategies
- [ ] Cost allocation and billing features
- [ ] Multi-level user hierarchies
