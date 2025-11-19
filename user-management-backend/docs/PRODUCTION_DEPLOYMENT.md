# Production Deployment Guide - EC2 with Docker

## 📍 Where GLM API Keys Are Stored

**IMPORTANT**: GLM API keys are **NOT stored in environment variables**. They are stored in **MongoDB** in the `User.glm_api_key` field.

### How It Works:
1. Users set their GLM API key via API:
   ```bash
   POST /api/users/me/glm-api-key?api_key=ghp_xxxxx
   Authorization: Bearer <clerk_token>
   ```

2. The key is stored in MongoDB in the user's document
3. The key is returned in the user profile:
   ```bash
   GET /api/users/me
   Response: { "glm_api_key": "ghp_xxxxx", ... }
   ```

### Database Location:
- **Collection**: `users`
- **Field**: `glm_api_key` (String, Optional)
- **Model**: `app/models/user.py` (line 43)

---

## 🚀 EC2 Deployment Steps

### 1. Prepare Your EC2 Instance

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for docker group to take effect
exit
```

### 2. Clone Your Repository

```bash
# Clone your repo (or use git pull if already cloned)
git clone https://github.com/your-username/backend-services.git
cd backend-services/user-management-backend
```

### 3. Create Production Environment File

```bash
# Copy example to .env
cp .env.example .env

# Edit with your production values
nano .env
```

### 4. Required Environment Variables

Edit `.env` with these **MANDATORY** values:

```bash
# CRITICAL - Change these!
JWT_SECRET_KEY=$(openssl rand -hex 32)  # Generate strong key
DEBUG=False
ENVIRONMENT=production

# Clerk Configuration (from Clerk Dashboard)
CLERK_JWKS_URL=https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json
CLERK_ISSUER=https://your-clerk-instance.clerk.accounts.dev
CLERK_AUDIENCE=https://your-production-domain.com

# Database (Docker internal URLs)
DATABASE_URL=mongodb://mongodb:27017/user_management_db
REDIS_URL=redis://redis:6379

# OAuth Providers (update with your production credentials)
GOOGLE_CLIENT_ID=your-prod-google-client-id
GOOGLE_CLIENT_SECRET=your-prod-google-client-secret
GOOGLE_REDIRECT_URI=https://your-domain.com/api/auth/google/callback

GITHUB_CLIENT_ID=your-prod-github-client-id
GITHUB_CLIENT_SECRET=your-prod-github-client-secret

# CORS - Add your frontend domain
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### 5. Deploy with Docker Compose

```bash
# Build and start services
docker-compose -f docker-compose.production.yml up --build -d

# Check logs
docker-compose -f docker-compose.production.yml logs -f api

# Check status
docker-compose -f docker-compose.production.yml ps
```

### 6. Configure Security Groups (AWS Console)

Allow these ports in your EC2 Security Group:
- **Port 80** (HTTP)
- **Port 443** (HTTPS)
- **Port 8000** (API - optional, if not using nginx)
- **Port 22** (SSH - restrict to your IP)

### 7. Set Up SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be in /etc/letsencrypt/live/your-domain.com/
```

### 8. Update CORS Settings

Edit `app/main.py` and update CORS origins:

```python
allow_origins=[
    "https://your-production-domain.com",
    "https://www.your-production-domain.com"
]
```

---

## 🔄 Updating Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml up --build -d

# View logs
docker-compose -f docker-compose.production.yml logs -f api
```

---

## 🔍 Monitoring & Logs

```bash
# View API logs
docker-compose -f docker-compose.production.yml logs -f api

# View MongoDB logs
docker-compose -f docker-compose.production.yml logs -f mongodb

# View Redis logs
docker-compose -f docker-compose.production.yml logs -f redis

# Check service health
curl http://localhost:8000/health

# Check database connection
docker exec -it user-management-backend-mongodb-1 mongosh
```

---

## 🛡️ Security Checklist

- [x] Changed `JWT_SECRET_KEY` to secure random value
- [x] Set `DEBUG=False` in production
- [x] Updated Clerk URLs to production instance
- [x] Configured CORS with actual frontend domains
- [x] Using HTTPS (SSL certificates)
- [x] Restricted Security Group ports
- [x] `.env` file is in `.gitignore`
- [x] OAuth redirect URIs updated to production URLs
- [x] Database has proper backups configured

---

## 📊 API Endpoints

### Health Check
```bash
GET http://your-domain.com/health
```

### User Profile (includes GLM API key)
```bash
GET /api/users/me
Authorization: Bearer <clerk_token>

Response:
{
  "id": "...",
  "email": "...",
  "glm_api_key": "ghp_xxxxx",  // User's GLM key
  "api_keys": [],
  ...
}
```

### Set GLM API Key
```bash
POST /api/users/me/glm-api-key?api_key=ghp_xxxxx
Authorization: Bearer <clerk_token>
```

---

## 🐛 Troubleshooting

### Container won't start
```bash
docker-compose -f docker-compose.production.yml logs api
```

### Database connection issues
```bash
# Check MongoDB is running
docker-compose -f docker-compose.production.yml ps mongodb

# Test connection
docker exec -it user-management-backend-mongodb-1 mongosh
```

### 401 Unauthorized errors
- Check Clerk configuration (JWKS URL, Issuer, Audience)
- Verify token is being sent in `Authorization: Bearer <token>` header
- Check logs: `docker-compose logs api | grep -i clerk`

---

## 📞 Support

For issues, check:
1. Docker logs: `docker-compose logs -f api`
2. Environment variables: `docker-compose config`
3. Health endpoint: `curl http://localhost:8000/health`
