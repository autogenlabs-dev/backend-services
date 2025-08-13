# Code Style and Conventions

## Python Code Style

### General Guidelines
- **PEP 8 Compliance** - Follow Python's official style guide
- **Type Hints** - Comprehensive type annotations for all functions and methods
- **Docstrings** - Detailed documentation for all classes and functions
- **Async/Await** - Consistent use of async programming patterns

### Naming Conventions
```python
# Classes: PascalCase
class UserManagement:
class ContentApproval:

# Functions and variables: snake_case
def get_current_user():
async def create_template():
user_id = "12345"

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_PAGE_SIZE = 50

# Private methods: _leading_underscore
def _validate_password():
async def _send_notification():
```

### Type Hints Usage
```python
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel

# Function signatures
async def get_user(user_id: str) -> Optional[User]:
    pass

def create_response(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"status": "success", "data": data}

# Class attributes
class User(Document):
    email: str
    created_at: datetime
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
```

### Docstring Format
```python
def approve_content(content_id: str, action: str, reason: Optional[str] = None) -> bool:
    """
    Approve or reject content in the marketplace.
    
    Args:
        content_id: Unique identifier for the content
        action: Either "approve" or "reject"
        reason: Optional reason for rejection
        
    Returns:
        bool: True if action was successful, False otherwise
        
    Raises:
        HTTPException: If content not found or invalid action
        
    Example:
        success = approve_content("12345", "approve")
    """
    pass
```

### Error Handling Patterns
```python
# Use specific exceptions
try:
    result = await some_operation()
except HTTPException:
    raise  # Re-raise HTTP exceptions
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Consistent error responses
raise HTTPException(
    status_code=404, 
    detail="Resource not found"
)
```

### Import Organization
```python
# Standard library imports
import asyncio
import sys
from datetime import datetime
from typing import Optional, List

# Third-party imports
from fastapi import FastAPI, HTTPException, Depends
from beanie import Document
from pydantic import BaseModel

# Local imports
from app.models.user import User
from app.middleware.auth import require_auth
```

## FastAPI Specific Conventions

### Endpoint Structure
```python
@app.get("/admin/users")
async def admin_get_users(
    request: Request,
    current_user: User = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100)
):
    """Get all users with pagination (Admin only)."""
    pass
```

### Response Models
```python
class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime
    is_active: bool
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## Database Model Conventions

### Beanie Document Structure
```python
class User(Document):
    """User model with comprehensive profile information."""
    
    # Required fields
    email: str = Field(..., index=True, description="User's email address")
    password_hash: str = Field(..., description="Hashed password")
    
    # Optional fields with defaults
    role: UserRole = Field(default=UserRole.USER, index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    class Settings:
        collection = "users"
        indexes = [
            "email",
            "role", 
            "created_at",
            ("email", "is_active")
        ]
```

### Field Validation
```python
from pydantic import validator, Field

class Template(Document):
    title: str = Field(..., min_length=3, max_length=100)
    pricing_inr: int = Field(default=0, ge=0)
    
    @validator('email')
    def validate_email(cls, v):
        return v.lower().strip()
```

## File Organization

### Directory Structure
```
app/
├── models/          # Database models
├── middleware/      # Authentication, rate limiting
├── utils/          # Helper functions, email service
├── api/            # API endpoint modules (if needed)
└── services/       # Business logic services
```

### Module Responsibilities
- **Models**: Pure data models with validation
- **Middleware**: Request/response processing
- **Utils**: Reusable helper functions
- **Services**: Business logic and external integrations