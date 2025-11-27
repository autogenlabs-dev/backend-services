# EC2 Production CORS Fix Guide

## Problem
Your template and component APIs are working locally but showing CORS errors on your EC2 production instance.

## Root Cause
Your production frontend domain is not in the allowed CORS origins list on the backend.

---

## Solution Options

### **Option 1: Update Environment Variable on EC2 (Recommended)**

This is the easiest fix without code changes. SSH into your EC2 instance and add the environment variable.

#### Steps:

1. **SSH into your EC2 instance:**
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

2. **Find your backend process:**
```bash
# If using systemd
sudo systemctl status your-backend-service

# If using PM2
pm2 list

# If using docker
docker ps
```

3. **Add the CORS_EXTRA_ORIGINS environment variable:**

**For systemd service:**
```bash
# Edit your service file
sudo nano /etc/systemd/system/your-backend.service

# Add this line under [Service] section:
Environment="CORS_EXTRA_ORIGINS=http://your-ec2-ip:3000,https://your-domain.com"

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart your-backend
```

**For PM2:**
```bash
# Create/edit ecosystem.config.js
nano ecosystem.config.js
```

Add this configuration:
```javascript
module.exports = {
  apps: [{
    name: "backend",
    script: "uvicorn",
    args: "app.main:app --host 0.0.0.0 --port 8000",
    env: {
      CORS_EXTRA_ORIGINS: "http://your-ec2-ip:3000,https://your-domain.com",
      ENVIRONMENT: "production"
    }
  }]
}
```

Then restart:
```bash
pm2 restart backend
```

**For Docker:**
```bash
# Add to docker-compose.yml or docker run command
docker run -e CORS_EXTRA_ORIGINS="http://your-ec2-ip:3000,https://your-domain.com" ...
```

**For direct process:**
```bash
# Add to your .bashrc or .profile
echo 'export CORS_EXTRA_ORIGINS="http://your-ec2-ip:3000,https://your-domain.com"' >> ~/.bashrc
source ~/.bashrc

# Or set it temporarily
export CORS_EXTRA_ORIGINS="http://your-ec2-ip:3000,https://your-domain.com"

# Restart your backend
```

---

### **Option 2: Update config.py (Permanent Fix)**

Add your production domain to the `backend_cors_origins` list in `config.py`.

1. **Edit config.py locally:**
```bash
cd /home/cis/Music/backend-services/user-management-backend/app
nano config.py
```

2. **Update line 52 to include your production domain:**
```python
# CORS
backend_cors_origins: List[str] = [
    "http://localhost:3000", 
    "http://localhost:3001", 
    "http://localhost:8080", 
    "https://codemurf.com", 
    "https://www.codemurf.com",
    "http://YOUR_EC2_IP:3000",           # Add your EC2 IP
    "https://YOUR_PRODUCTION_DOMAIN",     # Add your domain
]
```

3. **Commit and deploy:**
```bash
git add app/config.py
git commit -m "Add production CORS origins"
git push origin main

# On EC2, pull and restart
ssh your-ec2-instance
cd /path/to/backend-services/user-management-backend
git pull
# Restart your backend service
```

---

### **Option 3: Use .env.production File (Best Practice)**

1. **On your EC2 instance, create `.env.production`:**
```bash
cd /path/to/backend-services/user-management-backend
nano .env.production
```

2. **Add this configuration:**
```env
ENVIRONMENT=production
DEBUG=False
BACKEND_CORS_ORIGINS=["http://YOUR_EC2_IP:3000","https://YOUR_DOMAIN","https://www.YOUR_DOMAIN","https://codemurf.com"]
```

3. **Set environment variable to use production config:**
```bash
export ENVIRONMENT=production
```

4. **Restart your backend service**

---

## Quick Test Commands

### Test if CORS headers are being sent:
```bash
# Replace with your actual backend URL and frontend origin
curl -I -X OPTIONS \
  -H "Origin: http://your-frontend-domain:3000" \
  -H "Access-Control-Request-Method: GET" \
  http://your-backend-url:8000/api/templates

# Look for these headers in the response:
# Access-Control-Allow-Origin: http://your-frontend-domain:3000
# Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD
# Access-Control-Allow-Credentials: true
```

### Check backend logs:
```bash
# You should see this in logs when backend starts:
# 🔧 CORS Configuration:
#    - Allowed Origins: [list of origins]
#    - Debug Mode: False
```

---

## Common Production Domains to Add

Replace these with your actual values:

- `http://YOUR_EC2_PUBLIC_IP:3000` - If frontend runs on EC2
- `https://YOUR_DOMAIN.com` - Your production domain
- `https://www.YOUR_DOMAIN.com` - WWW variant
- `http://YOUR_EC2_PUBLIC_IP:8080` - If using different port

---

## Verification Checklist

- [ ] Added production domain to CORS origins
- [ ] Restarted backend service
- [ ] Checked backend startup logs for CORS configuration
- [ ] Tested API call from frontend
- [ ] Verified no CORS errors in browser console
- [ ] Checked Network tab shows correct CORS headers

---

## Need Help?

**Common Issues:**

1. **Still getting CORS error?**
   - Check exact origin in browser console (must match exactly)
   - Ensure protocol matches (http vs https)
   - Check for trailing slashes
   - Verify backend actually restarted

2. **Backend not restarting?**
   ```bash
   # Force kill and restart
   pkill -f uvicorn
   # Start again with your method (systemd, pm2, etc.)
   ```

3. **Environment variable not loading?**
   - Check if ENVIRONMENT=production is set
   - Verify .env.production exists in correct directory
   - Check file permissions: `chmod 644 .env.production`

---

## What Changed in the Code

The updated `main.py` now:
1. ✅ Loads CORS origins from `config.py` 
2. ✅ Adds development ports when in debug mode
3. ✅ Supports `CORS_EXTRA_ORIGINS` environment variable
4. ✅ Logs CORS configuration on startup for debugging

This means you can now configure CORS without changing code!
