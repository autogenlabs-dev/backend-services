# 🚨 QUICK FIX: CORS Error on Production

## Your Setup
- **EC2 Instance**: `ubuntu@ip-172-31-42-58`
- **Frontend**: `https://codemurf.com`
- **Backend**: `https://api.codemurf.com`

## ✅ Good News
Your domains (`codemurf.com` and `www.codemurf.com`) are **already configured** in the CORS settings!

## 🔧 You Just Need to Deploy the Updated Code

### **Option A: Automated Deployment (Recommended)**

```bash
cd /home/cis/Music/backend-services

# Make script executable
chmod +x deploy_to_ec2.sh

# Run deployment
./deploy_to_ec2.sh
```

Then follow the on-screen instructions to restart your backend.

---

### **Option B: Manual Steps**

#### Step 1: Push your changes to Git

```bash
cd /home/cis/Music/backend-services

git add user-management-backend/app/main.py
git commit -m "Fix CORS configuration for production"
git push origin main
```

#### Step 2: SSH to EC2 and update

```bash
ssh ubuntu@ip-172-31-42-58

# Once connected to EC2:
cd /home/ubuntu/backend-services/user-management-backend  # Or wherever your backend is
git pull origin main

# If using virtual environment:
source .venv/bin/activate  # or: source venv/bin/activate

# Install any updates
pip install -r requirements.txt
```

#### Step 3: Restart Backend

**Choose the method you're using:**

**PM2:**
```bash
pm2 restart backend
pm2 logs backend --lines 50
```

**systemd:**
```bash
sudo systemctl restart user-management-backend
sudo systemctl status user-management-backend
```

**Direct process:**
```bash
pkill -f uvicorn
cd /home/ubuntu/backend-services/user-management-backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

**Docker:**
```bash
docker-compose restart backend
docker-compose logs -f backend
```

#### Step 4: Verify CORS is working

Look for this in the logs when backend starts:
```
🔧 CORS Configuration:
   - Allowed Origins: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:8080', 'https://codemurf.com', 'https://www.codemurf.com']
   - Debug Mode: False
```

---

### **Option C: Test First (Before Deploying)**

Test from your local machine to see current CORS status:

```bash
cd /home/cis/Music/backend-services

# Test current production backend
./test_cors.sh https://api.codemurf.com https://codemurf.com
```

---

## 🧪 Verify the Fix

After restarting, test in your browser:

1. Open `https://codemurf.com`
2. Open browser DevTools (F12)
3. Go to Console tab
4. Try accessing templates or components API
5. **No CORS errors should appear!**

Or use curl:
```bash
curl -I -X OPTIONS \
  -H "Origin: https://codemurf.com" \
  -H "Access-Control-Request-Method: GET" \
  https://api.codemurf.com/api/templates
```

Look for:
```
access-control-allow-origin: https://codemurf.com
access-control-allow-credentials: true
```

---

## 🆘 If It Still Doesn't Work

### Check 1: Verify git repository is connected
```bash
ssh ubuntu@ip-172-31-42-58
cd /home/ubuntu/backend-services/user-management-backend
git remote -v
```

### Check 2: Force environment to production
```bash
ssh ubuntu@ip-172-31-42-58
export ENVIRONMENT=production
# Then restart backend
```

### Check 3: Add extra origins as fallback
```bash
ssh ubuntu@ip-172-31-42-58
export CORS_EXTRA_ORIGINS="https://codemurf.com,https://www.codemurf.com"
# Then restart backend
```

### Check 4: View backend logs
```bash
ssh ubuntu@ip-172-31-42-58

# PM2 logs
pm2 logs

# systemd logs
sudo journalctl -u user-management-backend -f

# Direct process logs
tail -f backend.log
```

---

## 📋 What Changed

The `main.py` CORS configuration now:
- ✅ Uses settings from `config.py` (which includes codemurf.com)
- ✅ Adds development ports automatically in debug mode
- ✅ Logs CORS configuration on startup
- ✅ Supports `CORS_EXTRA_ORIGINS` environment variable for flexibility

---

## Need More Help?

Check the full guide: [EC2_CORS_FIX_GUIDE.md](./EC2_CORS_FIX_GUIDE.md)
