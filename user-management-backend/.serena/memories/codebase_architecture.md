# Codebase Structure and Architecture

## Project Root Structure
```
backend-services/user-management-backend/
├── app/                          # Main application package
│   ├── models/                   # Database models (Beanie Documents)
│   ├── middleware/               # Request/response middleware
│   ├── utils/                    # Utility functions and services
│   ├── api/                      # API endpoint modules (organized)
│   ├── services/                 # Business logic services
│   ├── schemas/                  # Pydantic schemas for validation
│   └── auth/                     # Authentication utilities
├── tests/                        # Test files
├── alembic/                      # Database migration tools
├── memory-bank/                  # Project documentation and context
├── minimal_auth_server.py        # Main FastAPI application
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Container orchestration
├── Dockerfile                    # Container definition
└── *.py                         # Various utility and test scripts
```

## Core Application Architecture

### 1. Database Models (`app/models/`)
**Purpose**: Define data structures and database interactions

Key Models:
- `user.py` - User authentication and profiles
- `template.py` - Marketplace template items
- `component.py` - Marketplace component items
- `audit_log.py` - Admin action tracking
- `content_approval.py` - Content review workflow
- `developer_profile.py` - Developer-specific data
- `payment_transaction.py` - Financial transactions
- `purchased_item.py` - User purchase tracking

### 2. Middleware (`app/middleware/`)
**Purpose**: Request/response processing and authentication

Key Components:
- `auth.py` - Role-based access control and JWT validation
- `rate_limiting.py` - API rate limiting functionality

### 3. Utilities (`app/utils/`)
**Purpose**: Reusable helper functions and services

Key Components:
- `email_service.py` - Email notification system
- `password.py` - Password hashing utilities

### 4. Main Application (`minimal_auth_server.py`)
**Purpose**: FastAPI application with all endpoints

Sections:
- Database initialization (Beanie setup)
- Authentication endpoints
- User management endpoints
- Template/Component marketplace endpoints
- Admin dashboard endpoints (Phase 2)
- Payment processing endpoints

## Data Flow Architecture

### 1. Request Processing Flow
```
Client Request → CORS Middleware → Auth Middleware → Endpoint Handler → Database → Response
```

### 2. Authentication Flow
```
Login Request → Password Verification → JWT Generation → Token Storage → Protected Endpoint Access
```

### 3. Content Approval Workflow
```
Developer Creates Content → Set to Pending → Admin Reviews → Approve/Reject → Email Notification → Content Visibility Update
```

### 4. Role-Based Access Pattern
```
Request → Extract JWT → Validate User → Check Role → Allow/Deny Access → Audit Log (if admin action)
```

## Database Design

### Collections Structure
- **users** - User accounts with role-based access
- **templates** - Marketplace template items
- **components** - Marketplace component items
- **audit_logs** - Complete admin action tracking
- **content_approvals** - Content review workflow
- **developer_profiles** - Extended developer information
- **payment_transactions** - Financial transaction records
- **purchased_items** - User purchase tracking

### Indexing Strategy
- **Performance Indexes**: email, user_id, status, created_at
- **Compound Indexes**: (user_id, status), (timestamp, action_type)
- **Text Search**: title, description fields for content search

## API Endpoint Organization

### Public Endpoints (No Auth)
- `/` - Root endpoint
- `/health` - Health check
- `/register` - User registration
- `/login` - User authentication

### User Endpoints (Auth Required)
- `/templates` - Browse marketplace templates
- `/components` - Browse marketplace components
- `/templates/user/my-templates` - User's own templates
- `/user/profile` - User profile management

### Developer Endpoints (Developer Role)
- `POST /templates` - Create new templates
- `POST /components` - Create new components
- Template/Component CRUD operations

### Admin Endpoints (Admin Role Only)
- `/admin/users` - User management
- `/admin/developers` - Developer management
- `/admin/content/pending` - Content approval queue
- `/admin/content/approve/{id}` - Content approval actions
- `/admin/analytics` - Platform analytics
- `/admin/audit-logs` - Audit log viewing

## Key Design Patterns

### 1. Repository Pattern
- Models encapsulate database operations
- Beanie ODM provides async database access
- Consistent error handling across models

### 2. Dependency Injection
- FastAPI's Depends() for middleware injection
- Role-based access control through decorators
- Database session management

### 3. Observer Pattern
- Audit logging for admin actions
- Email notifications for state changes
- Event-driven architecture for workflow

### 4. Factory Pattern
- JWT token creation and validation
- Email notification generation
- Response formatting

## Security Architecture

### 1. Authentication Layers
- **JWT Tokens** - Stateless authentication
- **Password Hashing** - BCrypt for security
- **Role-Based Access** - Three-tier permission system

### 2. Authorization Matrix
| Role      | Content View | Content Create | Content Approve | Admin Access |
|-----------|-------------|----------------|-----------------|--------------|
| User      | Approved    | No             | No              | No           |
| Developer | All Own +   | Yes            | No              | No           |
|           | Approved    |                |                 |              |
| Admin     | All         | Yes            | Yes             | Yes          |

### 3. Audit Trail
- Complete action logging for compliance
- IP address and user agent tracking
- Timestamp and context preservation
- Admin dashboard for audit review