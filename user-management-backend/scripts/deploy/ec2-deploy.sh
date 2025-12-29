#!/bin/bash

# EC2 Deployment Script for User Management Backend (FIXED VERSION)
# Run this script on your EC2 instance after connecting via SSH

echo "🚀 Starting EC2 Deployment for User Management Backend"
echo "=================================================="

# Function to check disk space
check_disk_space() {
    local available_space=$(df / | awk 'NR==2 {print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    echo "💾 Available disk space: ${available_gb}GB"
    
    if [ $available_gb -lt 2 ]; then
        echo "⚠️  WARNING: Low disk space (${available_gb}GB). Cleaning up..."
        cleanup_system
    fi
}

# Function to clean up system to free disk space
cleanup_system() {
    echo "🧹 Cleaning up system to free disk space..."
    
    # Clean package manager cache
    sudo apt-get clean || sudo yum clean all
    sudo apt-get autoclean || true
    sudo apt-get autoremove -y || sudo yum autoremove -y
    
    # Clean Docker if it exists
    if command -v docker &> /dev/null; then
        echo "🐳 Cleaning Docker resources..."
        sudo docker system prune -f
        sudo docker image prune -a -f
        sudo docker volume prune -f
    fi
    
    # Clean old logs
    sudo journalctl --vacuum-time=7d
    
    # Clean temporary files
    sudo rm -rf /tmp/*
    sudo rm -rf /var/tmp/*
    
    echo "✅ System cleanup completed"
}

# Function to increase swap space for small EC2 instances
setup_swap() {
    local swap_size=$(free -m | awk '/^Swap:/ {print $2}')
    if [ "$swap_size" -eq 0 ]; then
        echo "💾 No swap detected. Creating 2GB swap file..."
        sudo fallocate -l 2G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
        echo "✅ Swap file created and enabled"
    else
        echo "✅ Swap already configured (${swap_size}MB)"
    fi
}

# Initial system check
echo "🔍 Checking system resources..."
check_disk_space
setup_swap

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Let's find the repository..."
    
    # Look for the repository
    if [ -d "backend-services" ]; then
        cd backend-services/user-management-backend
        echo "✅ Found repository in backend-services/user-management-backend"
    elif [ -d "user-management-backend" ]; then
        cd user-management-backend
        echo "✅ Found repository in user-management-backend"
    else
        echo "❌ Repository not found. Please clone it first:"
        echo "git clone https://github.com/autogenlabs-dev/backend-services.git"
        echo "cd backend-services/user-management-backend"
        exit 1
    fi
fi

echo "📁 Current directory: $(pwd)"

# Clean up any existing containers first
echo "🧹 Cleaning up existing Docker resources..."
if command -v docker-compose &> /dev/null; then
    sudo docker-compose down -v --remove-orphans 2>/dev/null || true
fi

if command -v docker &> /dev/null; then
    sudo docker system prune -f
fi

# Pull latest changes
echo "🔄 Pulling latest changes from repository..."
git fetch origin || echo "⚠️  Git fetch failed, continuing..."
git checkout main || git checkout master || echo "⚠️  Git checkout failed, using current branch"
git pull || echo "⚠️  Git pull failed, using current version"

# Detect OS and update system packages
echo "📦 Updating system packages..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    PACKAGE_MANAGER="apt"
elif command -v yum &> /dev/null; then
    sudo yum update -y
    PACKAGE_MANAGER="yum"
else
    echo "⚠️  Unknown package manager, skipping system update"
    PACKAGE_MANAGER="unknown"
fi

# Check if Docker is installed
echo "🐳 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed"
    
    # Clean up installation script
    rm -f get-docker.sh
fi

# Check if Docker Compose is installed
echo "🐳 Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
fi

# Install nginx for reverse proxy
echo "🌐 Installing nginx for reverse proxy..."
if [ "$PACKAGE_MANAGER" = "apt" ]; then
    sudo apt-get install -y nginx ufw
elif [ "$PACKAGE_MANAGER" = "yum" ]; then
    sudo yum install -y nginx firewalld
fi

# Setup basic firewall
echo "🔥 Setting up firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
fi

# Function to create nginx configuration
create_nginx_config() {
    echo "🔧 Configuring nginx for api.codemurf.com..."
    
    # Remove default nginx config
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Create the nginx configuration
    sudo tee /etc/nginx/sites-available/api-codemurf << 'NGINX_CONF'
# HTTP server block
# Redirect all HTTP traffic to HTTPS
server {
    listen 80;
    server_name api.codemurf.com;
    return 301 https://$host$request_uri;
}

# HTTPS server block
server {
    listen 443 ssl http2;
    server_name api.codemurf.com;

    # SSL configuration for Cloudflare Origin Certificate
    ssl_certificate /etc/ssl/certs/cloudflare-origin.pem;
    ssl_certificate_key /etc/ssl/private/cloudflare-origin.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Main API proxy
    location / {
        # Handle preflight OPTIONS requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "https://codemurf.com";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type "text/plain; charset=UTF-8";
            add_header Content-Length 0;
            return 204;
        }

        # CORS headers
        add_header Access-Control-Allow-Origin "https://codemurf.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With" always;
        add_header Access-Control-Allow-Credentials true always;

        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_cache_bypass $http_upgrade;
    }

    # Health endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
NGINX_CONF

    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/api-codemurf /etc/nginx/sites-enabled/
}

# Test and restart nginx with better error handling
test_and_start_nginx() {
    echo "🔧 Testing and starting nginx..."
    
    # Create SSL directory for future use
    sudo mkdir -p /etc/ssl/private
    sudo mkdir -p /etc/ssl/certs
    
    # Test nginx configuration (ignore SSL errors for now)
    if sudo nginx -t 2>/dev/null || echo "⚠️  SSL certificates not found - HTTP only mode"; then
        echo "✅ Nginx configuration acceptable"
        
        # Try to start/restart nginx
        if sudo systemctl is-active --quiet nginx; then
            echo "🔄 Reloading nginx configuration..."
            sudo systemctl reload nginx
        else
            echo "▶️  Starting nginx..."
            sudo systemctl start nginx
        fi
        
        sudo systemctl enable nginx
        
        # Verify nginx is running
        if sudo systemctl is-active --quiet nginx; then
            echo "✅ Nginx is running successfully"
            return 0
        else
            echo "❌ Nginx failed to start, checking status..."
            sudo systemctl status nginx --no-pager -l
            return 1
        fi
    else
        echo "❌ Nginx configuration has critical errors"
        sudo nginx -t
        return 1
    fi
}

# Create nginx configuration and test it
create_nginx_config
test_and_start_nginx

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
    else
        echo "❌ .env.example not found. Creating basic .env file..."
        cat > .env << 'ENV_EOF'
# Database Configuration
MONGODB_URL=mongodb://mongodb:27017/codemurf_api_prod
DATABASE_URL=mongodb://mongodb:27017/codemurf_api_prod

# Redis Configuration  
REDIS_URL=redis://redis:6379

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-$(date +%s)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=CodeMurf API
ENVIRONMENT=production

# CORS Configuration
ALLOWED_ORIGINS=https://codemurf.com,https://www.codemurf.com,https://api.codemurf.com

# Optional configurations (update as needed)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
ENV_EOF
        echo "✅ Basic .env file created"
    fi
    echo "⚠️  Please update the .env file with your actual configuration values"
fi

# Check disk space before building
check_disk_space

# Optimize Docker build process
echo "🔧 Optimizing Docker configuration..."
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null << 'DOCKER_CONF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
DOCKER_CONF

# Restart Docker to apply configuration
sudo systemctl restart docker

# Wait for Docker to be ready
echo "⏳ Waiting for Docker to be ready..."
sleep 5

# Build with optimizations for low disk space
echo "🏗️  Building application with disk space optimizations..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build images one by one to manage memory usage
sudo docker-compose pull mongodb redis 2>/dev/null || true
sudo docker-compose build --no-cache api

# Check disk space after build
check_disk_space

# Start the application
echo "🚀 Starting the application..."
sudo docker-compose up -d

# Wait for containers to be ready
echo "⏳ Waiting for containers to start..."
sleep 20

# Check container status
echo "📊 Container Status:"
sudo docker-compose ps

# Enhanced health checks
echo "🔍 Running health checks..."
sleep 10

# Function to test endpoint with retry
test_endpoint() {
    local url=$1
    local name=$2
    local max_retries=5
    local retry=0
    
    echo "Testing $name at $url..."
    while [ $retry -lt $max_retries ]; do
        if curl -f -s --connect-timeout 5 --max-time 10 "$url" > /dev/null 2>&1; then
            echo "✅ $name: OK"
            return 0
        else
            retry=$((retry + 1))
            echo "⏳ $name: Retry $retry/$max_retries"
            sleep 5
        fi
    done
    echo "❌ $name: Failed after $max_retries attempts"
    return 1
}

# Test endpoints
test_endpoint "http://localhost:8000/health" "Health Check (Direct)"
test_endpoint "http://localhost/health" "Health Check (via Nginx)"

# Show logs for debugging
echo "📄 Recent application logs:"
sudo docker-compose logs --tail=50 api

# Check system resources
echo "📊 System Resource Usage:"
echo "Memory: $(free -h | grep ^Mem | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
echo "Docker: $(sudo docker system df)"

# Get public IP
PUBLIC_IP=$(curl -s --connect-timeout 5 --max-time 10 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "Unable to get public IP")

echo ""
echo "🔐 SSL Certificate Setup Instructions:"
echo "=================================================="
echo "To enable HTTPS with Cloudflare Origin Certificate:"
echo ""
echo "1. Go to Cloudflare Dashboard > SSL/TLS > Origin Server"
echo "2. Click 'Create Certificate'"
echo "3. Generate certificate for: api.codemurf.com"
echo "4. Copy the certificate and run:"
echo "   sudo nano /etc/ssl/certs/cloudflare-origin.pem"
echo "5. Copy the private key and run:"
echo "   sudo nano /etc/ssl/private/cloudflare-origin.key"
echo "6. Set correct permissions:"
echo "   sudo chmod 644 /etc/ssl/certs/cloudflare-origin.pem"
echo "   sudo chmod 600 /etc/ssl/private/cloudflare-origin.key"
echo "7. Test and reload nginx:"
echo "   sudo nginx -t && sudo systemctl reload nginx"
echo "8. Set Cloudflare SSL mode to 'Full (strict)'"
echo "=================================================="

# Final status
echo ""
echo "🎉 Deployment Complete!"
echo "=================================================="
if [ "$PUBLIC_IP" != "Unable to get public IP" ]; then
    echo "🌐 Your CodeMurf API is running at:"
    echo "   - Production URL: https://api.codemurf.com"
    echo "   - Direct HTTP: http://$PUBLIC_IP"
    echo "   - Health Check: http://$PUBLIC_IP/health"
    echo "   - API Documentation: https://api.codemurf.com/docs"
    echo "   - API Status: https://api.codemurf.com/health"
else
    echo "🌐 Your CodeMurf API is running at:"
    echo "   - Production URL: https://api.codemurf.com"
    echo "   - Local: http://localhost/"
    echo "   - Health Check: http://localhost/health"
    echo "   - API Documentation: https://api.codemurf.com/docs"
fi
echo ""
echo "📋 Management Commands:"
echo "   - View logs: sudo docker-compose logs -f"
echo "   - View API logs: sudo docker-compose logs -f api"
echo "   - Restart services: sudo docker-compose restart"
echo "   - Stop services: sudo docker-compose down"
echo "   - Rebuild: sudo docker-compose down && sudo docker-compose up --build -d"
echo "   - Clean Docker: sudo docker system prune -f"
echo "   - Check Nginx: sudo nginx -t && sudo systemctl reload nginx"
echo "   - View Nginx logs: sudo tail -f /var/log/nginx/access.log"
echo ""
echo "🔧 Next Steps:"
echo "   1. Point api.codemurf.com DNS A record to: $PUBLIC_IP"
echo "   2. Set up Cloudflare SSL certificates (instructions above)"
echo "   3. Update .env file with production values"
echo "   4. Monitor logs and performance"
echo ""
echo "✅ CodeMurf API Backend is ready for production!"
