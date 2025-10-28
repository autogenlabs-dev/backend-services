# 🚀 Quick EC2 Setup Commands

## Problem: Missing Python Dependencies
```
ModuleNotFoundError: No module named 'motor'
```

## ⚡ Quick Solution (Run on your EC2 server):

### 🚨 UPDATED: Virtual Environment Required (Ubuntu 24.04+)

Since your system has externally-managed-environment protection, use this method:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies in virtual environment
pip install motor beanie pydantic fastapi python-dotenv asyncio-motor pymongo dnspython

# Test the installation
python3 -c "import motor.motor_asyncio; import beanie; print('✅ Ready!')"

# Run the database reset
python3 reset_live_db.py --confirm
```

### Alternative: System Override (Use with caution)
```bash
# Override system protection (not recommended but works)
pip3 install motor beanie pydantic fastapi python-dotenv --break-system-packages

# Run the database reset
python3 reset_live_db.py --confirm
```

### Option 3: Full Setup Script
```bash
# Make the install script executable and run it
chmod +x install-dependencies.sh
./install-dependencies.sh

# The script will handle virtual environment setup
```

## 🔍 Verification Commands

Check if dependencies are installed:
```bash
python3 -c "
import motor.motor_asyncio
import beanie
import pydantic
print('✅ All dependencies OK!')
"
```

Check if your app config works:
```bash
python3 -c "from app.config import Settings; print('✅ App config OK!')"
```

## 📋 Expected Output After Installation

```
🏭 LIVE DATABASE RESET & ACCOUNT CREATION
================================================================================

🔗 DATABASE CONNECTION INFO:
============================================================
🌐 Type: MongoDB Atlas (Cloud)
📍 Database: user_management_db
🏭 Environment: PRODUCTION

⚠️  DANGER ZONE ⚠️
============================================================
🚨 This will PERMANENTLY DELETE ALL DATA in the database!
🚨 This action CANNOT be undone!

🚨 CLEARING LIVE DATABASE...
============================================================
📍 Database: user_management_db
🗂️  Found X collections:
   - users
   - templates
   - ...

✅ Database cleared successfully!

🏭 CREATING PRODUCTION ACCOUNTS...
============================================================
✅ Created 👑 SUPERADMIN: superadmin@codemurf.com / SuperAdmin2025!@#
✅ Created 🛡️ ADMIN: admin@codemurf.com / Admin2025!@#  
✅ Created 💻 DEVELOPER: dev1@codemurf.com / Dev1Pass2025!
✅ Created 💻 DEVELOPER: dev2@codemurf.com / Dev2Pass2025!

🎉 SETUP COMPLETE!
```

## 🔒 Production Accounts Created

| Role | Email | Password |
|------|-------|----------|
| 👑 SUPERADMIN | superadmin@codemurf.com | SuperAdmin2025!@# |
| 🛡️ ADMIN | admin@codemurf.com | Admin2025!@# |
| 💻 DEV1 | dev1@codemurf.com | Dev1Pass2025! |
| 💻 DEV2 | dev2@codemurf.com | Dev2Pass2025! |

## 🚨 Database Connection Error Fix

If you see this error:
```
❌ Error clearing database: mongodb:27017: [Errno -3] Temporary failure in name resolution
```

**Problem:** Wrong database URL (pointing to local MongoDB instead of production)

### 🔧 Quick Fix:

```bash
# Check your current database configuration
bash debug-db-connection.sh

# If .env file is missing or has wrong DATABASE_URL, create it:
echo 'DATABASE_URL=mongodb+srv://your-atlas-connection-string' > .env

# Or if you have .env.production, copy it:
cp .env.production .env

# Then run the reset again:
python3 reset_live_db.py --confirm
```

### 📝 Correct .env file should look like:
```bash
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
# Not: mongodb://localhost:27017 or mongodb:27017
```

## 🧪 Test Your Accounts

After the reset, test login:
```bash
curl -X POST https://your-api-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@codemurf.com",
    "password": "SuperAdmin2025!@#"
  }'
```

---

**Ready to execute on your EC2 server!** 🎯