# 🐳 Live Database Reset & Production Account Setup

**Complete guide for clearing dockerized production database and creating essential accounts.**

---

## ⚠️ CRITICAL WARNING

**This will PERMANENTLY DELETE ALL DATA in your production database!**
- All user accounts will be removed
- All templates, components, and content will be deleted  
- All usage logs and analytics will be lost
- All API keys and tokens will be cleared

**This action cannot be undone. Ensure you have backups if needed.**

---

## 🎯 What Gets Created

After clearing the database, these accounts will be created:

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| 👑 **SUPERADMIN** | superadmin@codemurf.com | SuperAdmin2025!@# | System owner |
| 🛡️ **ADMIN** | admin@codemurf.com | Admin2025!@# | Platform manager |
| 💻 **DEV1** | dev1@codemurf.com | Dev1Pass2025! | Lead developer |
| 💻 **DEV2** | dev2@codemurf.com | Dev2Pass2025! | Senior developer |

---

## 🚀 Method 1: Direct Execution (Recommended)

### Step 1: Access Your Server
```bash
# SSH into your production server
ssh user@your-production-server.com
```

### Step 2: Navigate to Backend Directory
```bash
cd /path/to/user-management-backend
```

### Step 3: Run Database Reset
```bash
# Clear database and create accounts (with confirmation)
python3 reset_live_db.py

# Or skip confirmation prompts (use with extreme caution)
python3 reset_live_db.py --confirm
```

---

## 🐳 Method 2: Docker Container Execution

### Option A: From Host Machine
```bash
# If your backend runs in a Docker container
docker exec -it your-backend-container python3 reset_live_db.py --confirm

# Common container names:
docker exec -it backend-container python3 reset_live_db.py --confirm
docker exec -it user-management-backend python3 reset_live_db.py --confirm
docker exec -it app python3 reset_live_db.py --confirm
```

### Option B: Inside Container
```bash
# Enter the container first
docker exec -it your-backend-container bash

# Then run the script
python3 reset_live_db.py --confirm
```

### Option C: Docker Compose
```bash
# If using docker-compose
docker-compose exec backend python3 reset_live_db.py --confirm

# Or with service name
docker-compose exec user-management python3 reset_live_db.py --confirm
```

---

## 🔍 Method 3: Safe Mode Options

### Only Create Accounts (Don't Clear Database)
```bash
# Create accounts without clearing existing data
python3 reset_live_db.py --create-only
```

### Only Verify Existing Accounts
```bash
# Check what accounts currently exist
python3 reset_live_db.py --verify-only
```

### Docker Environment Detection
```bash
# Use Docker-aware version
python3 reset_live_db_docker.py --confirm
```

---

## 📋 Step-by-Step Execution

### 1. Preparation
```bash
# Check current database status
python3 reset_live_db.py --verify-only

# Backup database if needed (optional)
mongodump --uri="your-mongodb-connection-string"
```

### 2. Database Connection Check
The script will show your database connection:
```
🔗 DATABASE CONNECTION INFO:
============================================================
🌐 Type: MongoDB Atlas (Cloud)
📍 Database: user_management_db
🏭 Environment: PRODUCTION
```

### 3. Confirmation Process
When running without `--confirm`, you'll be prompted:
```
⚠️  DANGER ZONE ⚠️
============================================================
🚨 This will PERMANENTLY DELETE ALL DATA in the database!

Type 'DELETE ALL DATA' to confirm: DELETE ALL DATA
Are you absolutely sure? Type 'YES': YES
```

### 4. Execution Output
```
🚨 CLEARING LIVE DATABASE...
============================================================
📍 Database: user_management_db
🗂️  Found 8 collections:
   - users
   - templates
   - components
   - token_usage_logs
   - api_keys
   - subscriptions
   - oauth_accounts
   - template_categories

🗑️  Cleared users: 156 documents
🗑️  Cleared templates: 89 documents
🗑️  Cleared components: 34 documents
🗑️  Cleared token_usage_logs: 1,243 documents
🗑️  Cleared api_keys: 12 documents
🗑️  Cleared subscriptions: 23 documents
🗑️  Cleared oauth_accounts: 67 documents
🗑️  Cleared template_categories: 8 documents

✅ Database cleared successfully!

🏭 CREATING PRODUCTION ACCOUNTS...
============================================================
✅ Created 👑 SUPERADMIN:
   📧 Email: superadmin@codemurf.com
   👤 Name: System SuperAdmin
   🔑 Password: SuperAdmin2025!@#
   🎟️  Tokens: 50000

✅ Created 🛡️ ADMIN:
   📧 Email: admin@codemurf.com
   👤 Name: Platform Administrator
   🔑 Password: Admin2025!@#
   🎟️  Tokens: 50000

✅ Created 💻 DEVELOPER:
   📧 Email: dev1@codemurf.com
   👤 Name: Lead Developer
   🔑 Password: Dev1Pass2025!
   🎟️  Tokens: 50000

✅ Created 💻 DEVELOPER:
   📧 Email: dev2@codemurf.com
   👤 Name: Senior Developer
   🔑 Password: Dev2Pass2025!
   🎟️  Tokens: 50000
```

### 5. Verification
```
🔍 VERIFYING ACCOUNTS...
============================================================
📊 Total users created: 4

👑 SUPERADMIN (1 accounts):
   🟢 superadmin@codemurf.com - System SuperAdmin

🛡️ ADMIN (1 accounts):
   🟢 admin@codemurf.com - Platform Administrator

💻 DEVELOPER (2 accounts):
   🟢 dev1@codemurf.com - Lead Developer
   🟢 dev2@codemurf.com - Senior Developer

🎉 SETUP COMPLETE!
```

---

## 🧪 Testing Your Accounts

### Test Login via API
```bash
# Test SuperAdmin login
curl -X POST https://your-api-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@codemurf.com",
    "password": "SuperAdmin2025!@#"
  }'

# Test Admin login  
curl -X POST https://your-api-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@codemurf.com", 
    "password": "Admin2025!@#"
  }'

# Test Developer login
curl -X POST https://your-api-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev1@codemurf.com",
    "password": "Dev1Pass2025!"
  }'
```

### Test Frontend Login
1. Navigate to your web application
2. Use the credentials from the table above
3. Verify role-specific access:
   - **SuperAdmin**: Full system access
   - **Admin**: User management, content approval
   - **Developer**: Content creation, portfolio management

---

## 🔒 Post-Setup Security

### 1. Change Default Passwords
```bash
# Update passwords through your application
# Or use the user management API
curl -X PUT https://your-api-domain.com/api/v1/auth/password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_password": "YourNewSecurePassword123!"}'
```

### 2. Enable Additional Security
- Set up 2FA if available
- Configure IP restrictions for admin accounts
- Enable login monitoring and alerts
- Set up session timeouts

### 3. Monitor Account Activity
```bash
# Check recent logins
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://your-api-domain.com/api/v1/admin/users/activity
```

---

## 🚨 Troubleshooting

### Database Connection Issues
```bash
# Check MongoDB connection
python3 -c "
from app.config import Settings
settings = Settings()
print('Database URL:', settings.database_url)
"

# Test connection
python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import Settings

async def test():
    settings = Settings()
    client = AsyncIOMotorClient(settings.database_url)
    try:
        await client.admin.command('ismaster')
        print('✅ Database connection successful')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
    finally:
        client.close()

asyncio.run(test())
"
```

### Docker Container Issues
```bash
# List running containers
docker ps

# Check container logs
docker logs your-backend-container

# Access container shell
docker exec -it your-backend-container bash

# Check Python environment
docker exec -it your-backend-container python3 --version
```

### Permission Issues
```bash
# Check file permissions
ls -la reset_live_db.py

# Make script executable
chmod +x reset_live_db.py

# Run with sudo if needed (not recommended for production)
sudo python3 reset_live_db.py --confirm
```

---

## 📞 Quick Commands Reference

```bash
# Full reset with confirmation
python3 reset_live_db.py

# Full reset without confirmation (dangerous!)
python3 reset_live_db.py --confirm

# Only create accounts (safe)
python3 reset_live_db.py --create-only

# Only verify accounts (safe)
python3 reset_live_db.py --verify-only

# Docker version
python3 reset_live_db_docker.py --confirm

# Docker exec
docker exec -it backend-container python3 reset_live_db.py --confirm
```

---

## 📋 Final Checklist

- [ ] **Backup taken** (if needed)
- [ ] **Production environment confirmed**
- [ ] **Database URL verified** 
- [ ] **Script executed successfully**
- [ ] **4 accounts created** (1 superadmin, 1 admin, 2 developers)
- [ ] **Login tested** for all accounts
- [ ] **Passwords changed** from defaults
- [ ] **Security measures enabled**
- [ ] **Team notified** of new credentials

---

## 🎉 Success!

Your live database has been reset and production accounts are ready!

**Remember to:**
1. Change the default passwords immediately
2. Share credentials securely with your team
3. Set up proper security measures
4. Monitor account activity regularly

---

**Created:** October 10, 2025  
**Scripts:** `reset_live_db.py`, `reset_live_db_docker.py`  
**Environment:** Production/Live Database  
**Security:** Strong passwords, role-based access