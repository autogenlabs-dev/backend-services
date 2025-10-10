# 🎭 User Roles Summary

**Application:** User Management Backend + Autogenlabs Frontend  
**Total Roles:** 4 distinct user roles

---

## 📊 Role Hierarchy

| Role | Level | Access | Description |
|------|-------|---------|-------------|
| **SUPERADMIN** | 4 (Highest) | Full System Control | Ultimate system administrator |
| **ADMIN** | 3 | Platform Management | Content approval, user management |
| **DEVELOPER** | 2 | Content Creation | Can create/sell templates and components |
| **USER** | 1 (Basic) | Standard Access | Regular platform users |

---

## 🔧 Backend Implementation

### UserRole Enum (app/models/user.py)
```python
class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    DEVELOPER = "developer" 
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
```

### User Model Field
```python
class User(Document):
    # ... other fields ...
    role: UserRole = UserRole.USER  # Default role is USER
```

---

## 🎯 Role Permissions & Features

### 1. 👤 USER (Basic Role)
**Default role for new registrations**

✅ **Permissions:**
- Browse templates and components
- Download free content
- Purchase premium content
- Manage personal profile
- View own dashboard
- Use LLM proxy services
- Consume tokens (10,000 default)

❌ **Restricted:**
- Cannot create/upload content
- Cannot access admin features
- Cannot manage other users

### 2. 💻 DEVELOPER (Content Creator)
**Content creators and sellers**

✅ **All USER permissions PLUS:**
- Create and upload templates
- Create and upload components  
- Set pricing for premium content
- View sales analytics
- Manage content portfolio
- Access developer dashboard
- Receive earnings from sales

❌ **Restricted:**
- Cannot approve/reject content (needs admin approval)
- Cannot manage other users
- Cannot access platform settings

### 3. 🛡️ ADMIN (Platform Manager)
**Platform administrators**

✅ **All DEVELOPER permissions PLUS:**
- **User Management:**
  - View all users
  - Edit user roles (user ↔ developer ↔ admin)
  - Suspend/activate users
  - Delete users
  - View user details and analytics

- **Content Management:**
  - Approve/reject pending templates
  - Approve/reject pending components
  - Moderate content quality
  - Set rejection reasons
  - View content analytics

- **Platform Analytics:**
  - View platform-wide statistics
  - Monitor user activity
  - Track content performance
  - Generate reports

- **System Settings:**
  - Configure platform commission rates
  - Manage payment settings
  - Set content approval workflows

❌ **Restricted:**
- Cannot access superadmin features
- Limited system-level configurations

### 4. 👑 SUPERADMIN (System Owner)
**Ultimate system control**

✅ **All ADMIN permissions PLUS:**
- **System Administration:**
  - Manage admin users
  - Access server configurations
  - Database management
  - Security settings
  - System backups

- **Advanced Settings:**
  - API configurations
  - Integration settings
  - Server maintenance
  - System monitoring

---

## 🎨 Frontend Role Detection

### Role-Based UI (AdminDashboard.jsx)
```javascript
// Role-based filtering in user management
<select value={userFilter} onChange={(e) => setUserFilter(e.target.value)}>
    <option value="all">All Users</option>
    <option value="user">Regular Users</option>      {/* USER role */}
    <option value="developer">Developers</option>    {/* DEVELOPER role */}
    <option value="admin">Administrators</option>    {/* ADMIN role */}
</select>

// Role-based styling
<span className={`inline-block px-2 py-1 text-xs rounded-full ${
    user.role === 'admin' ? 'bg-red-500/20 text-red-400' :
    user.role === 'developer' ? 'bg-green-500/20 text-green-400' :
    'bg-blue-500/20 text-blue-400'  // USER role
}`}>
    {user.role}
</span>
```

### Protected Routes (ProtectedRoute.jsx)
```javascript
<ProtectedRoute requiredRole="admin">
    <AdminDashboard />
</ProtectedRoute>
```

---

## 🚀 Role Assignment & Management

### Default Assignment
- **New User Registration:** `USER` role by default
- **Role Upgrades:** Admin can promote users to higher roles
- **Role Downgrades:** Admin can demote users to lower roles

### Role Change Methods

#### 1. Admin Panel (Frontend)
- Navigate to Admin Dashboard → Users tab
- Click "Edit" button on user row
- Change role in dropdown (user/developer/admin)
- Save changes

#### 2. Backend Script (update_user_role.py)
```python
# Example usage
python3 update_user_role.py --email user@example.com --role developer
```

#### 3. Direct Database Update
```python
# In MongoDB
user = await User.find_one(User.email == "user@example.com")
user.role = UserRole.DEVELOPER
await user.save()
```

---

## 🔒 Security & Access Control

### Role Verification
```python
# Backend route protection
@router.get("/admin/users")
async def get_users(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
```

### Frontend Route Guards
```javascript
// AuthContext checks user role
const { user } = useAuth();
if (user?.role !== 'admin' && user?.role !== 'superadmin') {
    // Redirect or show error
}
```

---

## 📈 Role-Based Analytics

### Admin Dashboard Stats
- **Users by Role:** Count of users in each role
- **Developer Content:** Templates/components created by developers
- **Approval Queue:** Pending content awaiting admin approval
- **Revenue by Role:** Sales generated by developers

### Analytics Breakdown
```javascript
// Example admin analytics
{
    users: {
        total: 1250,
        by_role: {
            user: 1000,      // 80% regular users
            developer: 200,   // 16% content creators  
            admin: 49,       // 3.9% administrators
            superadmin: 1    // 0.1% system owners
        }
    }
}
```

---

## 🔄 Role Workflow Examples

### Content Creation Workflow
1. **DEVELOPER** creates template → Status: "pending"
2. **ADMIN** reviews template → Approve/Reject
3. **USER** can download approved template

### User Support Workflow  
1. **USER** reports issue
2. **ADMIN** investigates and resolves
3. **SUPERADMIN** handles escalated system issues

### Platform Management
1. **ADMIN** manages day-to-day operations
2. **SUPERADMIN** handles system configuration
3. Both monitor platform health and performance

---

## ⚙️ Configuration Files

### Backend (.env)
```env
# No specific role configurations needed
# Roles are handled in code logic
```

### Frontend Role Constants
```javascript
export const USER_ROLES = {
    USER: 'user',
    DEVELOPER: 'developer', 
    ADMIN: 'admin',
    SUPERADMIN: 'superadmin'
};
```

---

## 🎯 Quick Role Summary

| Feature | USER | DEVELOPER | ADMIN | SUPERADMIN |
|---------|------|-----------|-------|------------|
| Browse Content | ✅ | ✅ | ✅ | ✅ |
| Purchase Content | ✅ | ✅ | ✅ | ✅ |
| Create Content | ❌ | ✅ | ✅ | ✅ |
| Sell Content | ❌ | ✅ | ✅ | ✅ |
| Approve Content | ❌ | ❌ | ✅ | ✅ |
| User Management | ❌ | ❌ | ✅ | ✅ |
| Platform Analytics | ❌ | ❌ | ✅ | ✅ |
| System Administration | ❌ | ❌ | ❌ | ✅ |

---

## 📞 Role Management Commands

### Check User Role
```bash
# Backend
python3 check_users.py --email user@example.com

# Database query
db.users.findOne({email: "user@example.com"}, {role: 1, email: 1})
```

### Promote User
```bash
# Make user a developer
python3 update_user_role.py --email user@example.com --role developer

# Make user an admin  
python3 update_user_role.py --email user@example.com --role admin
```

### Bulk Role Assignment
```bash
# Make all users with email pattern developers
python3 bulk_update_roles.py --pattern "@company.com" --role developer
```

---

**Last Updated:** October 10, 2025  
**Backend Model:** `/home/cis/Music/backend-services/user-management-backend/app/models/user.py`  
**Frontend Dashboard:** `/home/cis/Music/Autogenlabs-Web-App/src/components/pages/dashboard/AdminDashboard.jsx`  
**Role Management:** Available in admin panel and backend scripts