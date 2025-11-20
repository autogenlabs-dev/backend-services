# 🚀 Production Deployment Checklist

## Pre-Deployment Preparation

### 1. Environment Configuration ✅

Create `.env.production` file with the following **CRITICAL** settings:

#### **Must Configure:**
```bash
# 1. Generate secure JWT secret
openssl rand -hex 32
# Add to: JWT_SECRET_KEY=<generated_key>

# 2. Update Clerk credentials (from dashboard.clerk.com)
CLERK_ISSUER=https://your-instance.clerk.accounts.dev
CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
CLERK_SECRET_KEY=sk_live_xxxxx

# 3. OpenRouter Provisioning Key (CRITICAL for user API keys)
OPENROUTER_PROVISIONING_API_KEY=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

# 4. Update Production URLs
PRODUCTION_BACKEND_URL=https://api.codemurf.com
PRODUCTION_FRONTEND_URL=https://codemurf.com
API_ENDPOINT=https://api.codemurf.com

# 5. CORS Origins (add your production domains)
BACKEND_CORS_ORIGINS=["https://codemurf.com","https://www.codemurf.com","https://api.codemurf.com"]

# 6. Set Production Mode
DEBUG=False
ENVIRONMENT=production
```

### 2. Database Setup ✅

Your current MongoDB Atlas connection is already configured:
```
DATABASE_URL=mongodb+srv://autogencodebuilder:DataOnline@autogen.jf0j0.mongodb.net/user_management_db
```

**Verify:**
- [ ] Database user has proper read/write permissions
- [ ] Network access allows production server IPs
- [ ] Connection string includes retry and timeout parameters

### 3. Clerk Configuration (Frontend & Backend) ✅

**Clerk Dashboard Setup:**
1. Go to https://dashboard.clerk.com
2. Select your production application
3. Navigate to **API Keys** section
4. Copy these values:
   - **Publishable Key** (for frontend): `pk_live_xxx`
   - **Secret Key** (for backend): `sk_live_xxx`
   - **JWKS URL**: Should be `https://your-instance.clerk.accounts.dev/.well-known/jwks.json`

5. **Important:** Configure allowed redirect URLs in Clerk:
   - Add: `https://codemurf.com/*`
   - Add: `https://api.codemurf.com/api/auth/clerk/callback`

**Frontend Configuration:**
Update your Next.js `.env.local`:
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxxxx
CLERK_SECRET_KEY=sk_live_xxxxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### 4. Security Checklist ✅

- [ ] Generate new JWT secret (don't use development key)
- [ ] Update Clerk keys to production keys
- [ ] Set `DEBUG=False`
- [ ] Configure HTTPS redirects
- [ ] Set up SSL certificates (Let's Encrypt recommended)
- [ ] Enable CORS only for trusted domains
- [ ] Review and update rate limiting settings

### 5. Infrastructure Setup ✅

**Docker Deployment (Recommended):**
```bash
# 1. Copy production environment file
cp .env.production.example .env.production
# Edit .env.production with your values

# 2. Build production container
docker-compose -f docker-compose.production.yml build

# 3. Start services
docker-compose -f docker-compose.production.yml up -d

# 4. Check logs
docker-compose -f docker-compose.production.yml logs -f api
```

**Or EC2/VPS Deployment:**
```bash
# 1. Clone repository
git clone <your-repo>
cd user-management-backend

# 2. Setup environment
cp .env.production.example .env.production
# Edit .env.production

# 3. Install dependencies
pip install -r requirements-production.txt

# 4. Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 6. DNS & SSL Configuration ✅

**Required DNS Records:**
```
api.codemurf.com    A    <your-server-ip>
www.codemurf.com    A    <your-server-ip>
codemurf.com        A    <your-server-ip>
```

**SSL Certificate (Let's Encrypt):**
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d api.codemurf.com -d codemurf.com -d www.codemurf.com
```

### 7. Nginx Reverse Proxy Configuration ✅

Create `/etc/nginx/sites-available/api.codemurf.com`:
```nginx
server {
    listen 80;
    server_name api.codemurf.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.codemurf.com;

    ssl_certificate /etc/letsencrypt/live/api.codemurf.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.codemurf.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/api.codemurf.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Post-Deployment Verification

### 1. Health Check ✅
```bash
curl https://api.codemurf.com/health
# Expected: {"status":"ok"}
```

### 2. Test Authentication ✅
```bash
# Get a fresh Clerk token from your frontend
curl -H "Authorization: Bearer <clerk_token>" https://api.codemurf.com/api/users/me
```

### 3. Test OpenRouter Key Provisioning ✅
```bash
curl -X POST https://api.codemurf.com/api/users/me/openrouter-key/refresh \
  -H "Authorization: Bearer <clerk_token>"
# Should return: {"openrouter_api_key": "sk-or-v1-xxx..."}
```

### 4. Verify Subscription Plans ✅
```bash
curl -H "Authorization: Bearer <clerk_token>" https://api.codemurf.com/api/users/me | jq '.subscription'
# Expected: "free" (default for new users)
```

### 5. Monitor Logs
```bash
# Docker deployment
docker-compose logs -f api

# Or systemd service
sudo journalctl -u user-management-backend -f
```

---

## Environment Variables Summary

### **CRITICAL - Must Change:**
1. ✅ `JWT_SECRET_KEY` - Generate with `openssl rand -hex 32`
2. ✅ `CLERK_ISSUER` - Your Clerk instance URL
3. ✅ `CLERK_JWKS_URL` - Your Clerk JWKS endpoint
4. ✅ `CLERK_SECRET_KEY` - Production secret key from Clerk
5. ✅ `OPENROUTER_PROVISIONING_API_KEY` - Already have: `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`
6. ✅ `DEBUG=False`
7. ✅ `ENVIRONMENT=production`

### **Important - Should Update:**
- `BACKEND_CORS_ORIGINS` - Add production domains
- `PRODUCTION_BACKEND_URL` - Your API domain
- `PRODUCTION_FRONTEND_URL` - Your frontend domain
- `DATABASE_URL` - Already configured with MongoDB Atlas

### **Optional - Add if Using:**
- OAuth: `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`
- Payments: `STRIPE_SECRET_KEY`, `RAZORPAY_KEY_ID`
- Other LLM providers: `GLAMA_API_KEY`, etc.

---

## Quick Deployment Commands

```bash
# 1. Copy and configure environment
cp .env.production.example .env.production
nano .env.production  # Edit with your values

# 2. Deploy with Docker
docker-compose -f docker-compose.production.yml up -d --build

# 3. Check status
docker-compose ps
curl https://api.codemurf.com/health

# 4. View logs
docker-compose logs -f api
```

---

## Monitoring & Maintenance

### Health Checks
- Health endpoint: `https://api.codemurf.com/health`
- API docs: `https://api.codemurf.com/docs` (disable in production if sensitive)

### Database Backups
```bash
# MongoDB Atlas automated backups are enabled by default
# Verify in Atlas dashboard: Data Storage > Backup
```

### Log Rotation
```bash
# For Docker logs
docker-compose logs --tail=100 api > api.log
```

---

## Troubleshooting

### Issue: "Token has expired"
- Check Clerk token expiration settings
- Verify frontend is using correct Clerk instance
- Ensure system time is synchronized (NTP)

### Issue: "OpenRouter key returns null"
- Verify `OPENROUTER_PROVISIONING_API_KEY` is set
- Check container logs for provisioning errors
- Test provisioning key manually with curl

### Issue: "CORS error"
- Add frontend domain to `BACKEND_CORS_ORIGINS`
- Verify Nginx proxy headers are set correctly
- Check browser console for exact CORS error

---

## Need Help?

1. Check logs: `docker-compose logs -f api`
2. Verify environment: `docker-compose config`
3. Test connectivity: `curl -v https://api.codemurf.com/health`
