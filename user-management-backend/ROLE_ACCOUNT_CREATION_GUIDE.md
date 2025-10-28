# 🎭 How to Create Developer, Admin & SuperAdmin Accounts

This guide shows you **4 different methods** to create accounts with elevated roles in your User Management Backend.

---

## 🚀 Method 1: Quick Setup (Recommended for Testing)

**Creates sample accounts for all 4 roles instantly:**

```bash
cd /home/cis/Music/backend-services/user-management-backend

# Create all role accounts at once
python3 quick_setup_roles.py
```

**This creates:**
- 👤 **USER:** user@codemurf.com / userpass123
- 💻 **DEVELOPER:** developer@codemurf.com / devpass123  
- 🛡️ **ADMIN:** admin@codemurf.com / adminpass123
- 👑 **SUPERADMIN:** superadmin@codemurf.com / superpass123

---

## ⚡ Method 2: Interactive Account Manager

**Full-featured script with interactive menus:**

```bash
# Run the comprehensive account manager
python3 create_role_accounts.py
```

**Menu options:**
1. **Create sample accounts** - Same as quick setup
2. **List existing users** - See all users by role
3. **Create custom account** - Enter your own details
4. **Update user role** - Change existing user's role

---

## 🎯 Method 3: Command Line (Direct)

**Create specific accounts with command line arguments:**

```bash
# Create a developer account
python3 create_role_accounts.py \
  --email "john@company.com" \
  --password "mypassword" \
  --role "developer" \
  --name "John Developer"

# Create an admin account  
python3 create_role_accounts.py \
  --email "sarah@company.com" \
  --password "adminpass" \
  --role "admin" \
  --name "Sarah Administrator"

# Create a superadmin account
python3 create_role_accounts.py \
  --email "owner@company.com" \
  --password "superpass" \
  --role "superadmin" \
  --name "System Owner"
```

**Update existing user role:**
```bash
# Change user to developer
python3 create_role_accounts.py \
  --email "existing@user.com" \
  --role "developer" \
  --update

# Promote to admin
python3 create_role_accounts.py \
  --email "developer@company.com" \
  --role "admin" \
  --update
```

---

## 🔧 Method 4: Admin Panel (Frontend)

**Use your web interface to manage roles:**

1. **Create admin account first** (using Method 1, 2, or 3)

2. **Login to frontend** at your web app URL

3. **Navigate to Admin Dashboard:**
   - Login with admin credentials
   - Go to "Users" tab
   - Click "Edit" on any user
   - Change role in dropdown
   - Save changes

**Admin Panel Features:**
- ✅ View all users by role
- ✅ Edit user roles (user ↔ developer ↔ admin)
- ✅ Suspend/activate users
- ✅ Delete users
- ✅ User analytics

---

## 📊 Verify Your Accounts

**List all users by role:**
```bash
python3 create_role_accounts.py --list
```

**Check specific user:**
```bash
python3 check_users.py --email "admin@codemurf.com"
```

**Test login via API:**
```bash
# Test admin login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@codemurf.com",
    "password": "adminpass123"
  }'
```

---

## 🎯 Role-Specific Features

### 👤 USER Account
**What they can do:**
- Browse templates and components
- Download free content  
- Purchase premium content
- Use LLM proxy (10,000 tokens)
- Manage personal profile

**Test endpoints:**
```bash
# Get profile
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/profile

# Browse templates  
curl http://localhost:8000/api/v1/templates
```

### 💻 DEVELOPER Account  
**Additional capabilities:**
- Create and upload templates
- Set pricing for content
- View sales analytics
- Access developer dashboard

**Test endpoints:**
```bash
# Create template (developer only)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Template","category":"web"}' \
  http://localhost:8000/api/v1/templates
```

### 🛡️ ADMIN Account
**Management capabilities:**
- Approve/reject content
- Manage all users
- View platform analytics
- Configure settings

**Test endpoints:**
```bash
# Get all users (admin only)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/admin/users

# Approve content (admin only)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"status":"approved"}' \
  http://localhost:8000/api/v1/admin/content/123/approve
```

### 👑 SUPERADMIN Account
**Full system control:**
- All admin capabilities
- System configuration
- Server management
- Database access

---

## 🔐 Security Notes

### Password Requirements
- **Minimum 8 characters** recommended
- **Mix of letters, numbers, symbols** for production
- **Default test passwords** should be changed in production

### Role Assignment Rules
- **USER** → **DEVELOPER**: Self-service or admin approval
- **DEVELOPER** → **ADMIN**: Admin/SuperAdmin only
- **ADMIN** → **SUPERADMIN**: SuperAdmin only
- **Demotion**: Reverse process applies

### Production Considerations
```bash
# Change default passwords
python3 create_role_accounts.py \
  --email "admin@yourcompany.com" \
  --password "StrongP@ssw0rd123!" \
  --role "admin" \
  --name "Your Admin Name"
```

---

## 🚨 Troubleshooting

### Common Issues

**1. "User already exists"**
```bash
# Update existing user instead
python3 create_role_accounts.py \
  --email "existing@user.com" \
  --role "admin" \
  --update
```

**2. Database connection error**
```bash
# Check if server is running
curl http://localhost:8000/health

# Check .env configuration
cat .env | grep DATABASE_URL
```

**3. Import errors**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python path
python3 -c "from app.models.user import User; print('OK')"
```

**4. Role not recognized**
```bash
# Valid roles (case-sensitive):
# - user
# - developer  
# - admin
# - superadmin
```

---

## 📋 Quick Reference Commands

```bash
# Quick setup all roles
python3 quick_setup_roles.py

# Interactive manager
python3 create_role_accounts.py

# Create developer
python3 create_role_accounts.py --email "dev@test.com" --role "developer" --password "devpass"

# Create admin  
python3 create_role_accounts.py --email "admin@test.com" --role "admin" --password "adminpass"

# Create superadmin
python3 create_role_accounts.py --email "super@test.com" --role "superadmin" --password "superpass"

# Update role
python3 create_role_accounts.py --email "user@test.com" --role "developer" --update

# List users
python3 create_role_accounts.py --list

# Check specific user
python3 check_users.py --email "admin@test.com"
```

---

## 🎉 Next Steps

1. **Create accounts** using your preferred method
2. **Test login** via API or frontend  
3. **Verify permissions** by accessing role-specific features
4. **Set up production accounts** with strong passwords
5. **Configure admin panel access** in your frontend

**Your role system is ready! 🚀**

---

**Created:** October 10, 2025  
**Scripts Location:** `/home/cis/Music/backend-services/user-management-backend/`  
**Frontend Admin:** Available in your Autogenlabs-Web-App admin dashboard