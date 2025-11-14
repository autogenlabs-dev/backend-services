# Docker Google OAuth Testing Guide

## 🐳 Docker-Specific Testing Instructions

Since you're running the backend with Docker, here are the specific commands and considerations for testing Google OAuth:

## 🚀 Quick Docker Commands

### Start Backend Container

```bash
# Navigate to backend directory
cd user-management-backend

# Build and run with Docker (choose one method)
# Method 1: Using docker-compose
docker-compose up --build

# Method 2: Using Dockerfile directly
docker build -t user-management-backend .
docker run -p 8000:8000 --name oauth-backend user-management-backend

# Method 3: If you have existing container
docker start oauth-backend
```

### View Container Logs

```bash
# View logs of running container
docker logs -f oauth-backend

# View logs in real-time
docker logs -f oauth-backend

# View logs with timestamps
docker logs -f oauth-backend --since="2025-11-06T11:30"
```

### Stop Backend Container

```bash
# Stop the container
docker stop oauth-backend

# Remove container (optional)
docker rm oauth-backend
```

### Access Container Shell (for debugging)

```bash
# Access running container shell
docker exec -it oauth-backend /bin/bash

# Install additional tools if needed
docker exec -it oauth-backend apt-get update && apt-get install -y curl
```

## 🧪 Docker-Specific Testing Process

### 1. Verify Container is Running

```bash
# Check if container is running
docker ps | grep oauth-backend

# Check container status
docker inspect oauth-backend | jq '.[0].State.Status'
```

### 2. Test OAuth Flow with Docker

```bash
# Test OAuth login endpoint from outside container
curl -I http://localhost:8000/api/auth/google/login

# Test OAuth providers endpoint
curl -I http://localhost:8000/api/auth/providers

# Test health endpoint
curl -I http://localhost:8000/health
```

### 3. Debug Inside Container

```bash
# Access container shell for debugging
docker exec -it oauth-backend /bin/bash

# Check environment variables inside container
docker exec oauth-backend env | grep GOOGLE

# Check if OAuth configuration is loaded
docker exec oauth-backend python -c "
from app.config import settings
print('Google Client ID:', settings.google_client_id)
print('Environment:', settings.environment)
"

# Test OAuth flow inside container
docker exec oauth-backend python -c "
import httpx
import asyncio

async def test_oauth():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('http://localhost:8000/api/auth/providers')
            print('Providers:', response.json())
    except Exception as e:
        print('Error:', e)

asyncio.run(test_oauth())
"
```

## 🔍 Docker-Specific Issues and Solutions

### Issue 1: Port Mapping Problems

**Problem**: Container port not mapped correctly to host

**Symptoms**:
- Connection refused when accessing `http://localhost:8000`
- OAuth login redirects fail

**Solution**:
```bash
# Check port mapping
docker port oauth-backend

# Ensure correct port mapping
docker run -p 8000:8000 --name oauth-backend user-management-backend

# Or use docker-compose with correct ports
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
```

### Issue 2: Environment Variables Not Loaded

**Problem**: Environment variables not passed to Docker container

**Symptoms**:
- OAuth provider not configured errors
- Google client ID showing as placeholder

**Solution**:
```bash
# Method 1: Using .env file
docker run --env-file .env -p 8000:8000 --name oauth-backend user-management-backend

# Method 2: Using docker-compose
docker-compose up --env-file .env

# Method 3: Pass environment directly
docker run -e GOOGLE_CLIENT_ID=your-id -e GOOGLE_CLIENT_SECRET=your-secret -p 8000:8000 --name oauth-backend user-management-backend
```

### Issue 3: Container Network Isolation

**Problem**: Container can't reach Google OAuth from localhost

**Symptoms**:
- Timeouts during token exchange
- Network connectivity errors

**Solution**:
```bash
# Use host networking mode
docker run --network="host" -p 8000:8000 --name oauth-backend user-management-backend

# Or add to docker-compose
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    network_mode: "host"
```

## 🐳 Docker Compose Configuration

Create this `docker-compose.oauth.yml` for OAuth testing:

```yaml
version: '3.8'

services:
  oauth-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - ENVIRONMENT=development
    volumes:
      - ./logs:/app/logs
    network_mode: "host"
    restart: unless-stopped
```

## 📋 Docker Testing Script

Create this `test-oauth-docker.sh` script:

```bash
#!/bin/bash

echo "🐳 Docker Google OAuth Testing"
echo "=========================="

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not running. Please install Docker first."
    exit 1
fi

# Navigate to backend directory
cd user-management-backend

# Stop any existing container
echo "🛑 Stopping existing containers..."
docker stop oauth-backend 2>/dev/null || true
docker rm oauth-backend 2>/dev/null || true

# Build and start with Docker Compose
echo "🚀 Starting OAuth backend with Docker Compose..."
docker-compose -f docker-compose.oauth.yml up -d

# Wait for container to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Test OAuth endpoints
echo "🔍 Testing OAuth endpoints..."

# Test health endpoint
echo "1. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health | jq '.status' 2>/dev/null)
if [ "$HEALTH_RESPONSE" = "\"healthy\"" ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed: $HEALTH_RESPONSE"
fi

# Test providers endpoint
echo "2. Testing providers endpoint..."
PROVIDERS_RESPONSE=$(curl -s http://localhost:8000/api/auth/providers | jq '.providers' 2>/dev/null)
if [ -n "$PROVIDERS_RESPONSE" ]; then
    echo "✅ Providers check passed"
    echo "Available providers: $PROVIDERS_RESPONSE"
else
    echo "❌ Providers check failed"
fi

# Test OAuth login initiation
echo "3. Testing OAuth login initiation..."
LOGIN_RESPONSE=$(curl -s -I http://localhost:8000/api/auth/google/login | grep -i location | cut -d' ' -f2)
if [ -n "$LOGIN_RESPONSE" ]; then
    echo "✅ OAuth login initiation passed"
    echo "Redirect URL: $LOGIN_RESPONSE"
else
    echo "❌ OAuth login initiation failed"
fi

# Show container logs
echo "📋 Container logs:"
docker logs oauth-backend --tail=20

echo "=========================="
echo "🌐 Open http://localhost:3000 in your browser"
echo "🔍 Click 'Login with Google' to test the complete OAuth flow"
echo "📊 Monitor this terminal for backend logs"
echo "📱 Check browser network tab for HTTP requests"
```

Make it executable:
```bash
chmod +x test-oauth-docker.sh
./test-oauth-docker.sh
```

## 🔍 Docker Debugging Commands

### Check Container Environment

```bash
# Check all environment variables
docker exec oauth-backend env

# Check specific OAuth variables
docker exec oauth-backend env | grep GOOGLE

# Check if configuration file is mounted
docker exec oauth-backend ls -la /app/.env
```

### Monitor Real-time Logs

```bash
# Follow logs in real-time
docker logs -f oauth-backend

# Filter logs for OAuth-related messages
docker logs oauth-backend | grep -E "(OAuth|google|callback|token)"

# Save logs to file
docker logs oauth-backend > oauth-debug.log 2>&1 &
```

### Access Container for Debugging

```bash
# Start a shell session in the container
docker exec -it oauth-backend /bin/bash

# Install debugging tools
docker exec oauth-backend apt-get update && apt-get install -y vim curl

# Edit files inside container
docker exec oauth-backend vim app/config.py

# Restart services inside container
docker exec oauth-backend supervisorctl restart uvicorn
```

## 🎯 Docker Production Considerations

### Environment Variables
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  oauth-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - ENVIRONMENT=production
      - MONGODB_URL=${MONGODB_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### Security Settings
```yaml
# Add security considerations
services:
  oauth-backend:
    build: .
    ports:
      - "127.0.0.1:8000:8000"  # Bind to localhost only
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
    security_opt:
      - no-new-privileges:true
```

## 📊 Expected Docker Test Output

```
🐳 Docker Google OAuth Testing
==========================
🛑 Stopping existing containers...
🚀 Starting OAuth backend with Docker Compose...
⏳ Waiting for backend to be ready...
🔍 Testing OAuth endpoints...
1. Testing health endpoint...
✅ Health check passed
2. Testing providers endpoint...
✅ Providers check passed
Available providers: [{"name": "google", "display_name": "Google", "authorization_url": "/api/auth/google/login"}]
3. Testing OAuth login initiation...
✅ OAuth login initiation passed
Redirect URL: https://accounts.google.com/o/oauth2/auth?client_id=...&redirect_uri=http://localhost:8000/api/auth/google/callback&response_type=code&scope=openid+email+profile&state=...
📋 Container logs:
[timestamp] OAuth callback for google
[timestamp] Callback URL: http://localhost:8000/api/auth/google/callback?code=...&state=...
[timestamp] Authorization code received: ...
[timestamp] Token exchange successful!
[timestamp] JWT tokens created for user ...
==========================
🌐 Open http://localhost:3000 in your browser
🔍 Click 'Login with Google' to test the complete OAuth flow
📊 Monitor this terminal for backend logs
📱 Check browser network tab for HTTP requests
```

## 🚀 Quick Docker Commands Reference

```bash
# Build image
docker build -t user-management-backend .

# Run container with environment file
docker run --env-file .env -p 8000:8000 user-management-backend

# View logs
docker logs -f oauth-backend

# Access container
docker exec -it oauth-backend /bin/bash

# Stop container
docker stop oauth-backend

# Clean up
docker system prune -f
```

Use this Docker-specific guide to test your Google OAuth flow in the containerized environment!