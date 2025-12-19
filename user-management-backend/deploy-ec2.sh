#!/bin/bash
# Minimal EC2 Deployment Script for FastAPI Backend
# Optimized to avoid dependency conflicts

set -e  # Exit on any error

echo "🚀 Starting Minimal FastAPI Backend Deployment on EC2..."

# Update system packages (ignore warnings)
sudo apt update 2>/dev/null || true

# Install only essential system dependencies
echo "📦 Installing minimal system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    nginx \
    software-properties-common

# Install MongoDB using snap (avoids apt key issues)
echo "📦 Installing MongoDB via snap..."
sudo snap install mongodb

# Start MongoDB
sudo snap start mongodb
sudo snap enable mongodb

# Install Redis (minimal)
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Create application directory
APP_DIR="/home/ubuntu/fastapi-backend"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone repository
if [ ! -d "$APP_DIR/.git" ]; then
    cd /home/ubuntu
    git clone https://github.com/autogenlabs-dev/backend-services.git fastapi-backend
    cd fastapi-backend/user-management-backend
else
    cd $APP_DIR/user-management-backend
    git pull origin main
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies with minimal extras
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create minimal environment file
if [ ! -f .env ]; then
    echo "📝 Creating minimal .env file..."
    cat > .env << EOF
# Minimal Configuration
DATABASE_URL=mongodb://localhost:27017/user_management_db
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=0b1ae784667db0d6e1c241624640f3b23fc909adf1b03760b6a1568ac96392f2d39513e651dbaa8d435661953ac8eaed6712aa8ed3071747c210cb990e08f2b4
JWT_ALGORITHM=HS256
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=["*"]
EOF
fi

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/fastapi.service > /dev/null << EOF
[Unit]
Description=FastAPI Backend
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=$APP_DIR/user-management-backend
Environment=PATH=$APP_DIR/user-management-backend/venv/bin
ExecStart=$APP_DIR/user-management-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create minimal nginx config
echo "🌐 Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/fastapi > /dev/null << EOF
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
EOF

# Remove default nginx site and enable ours
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi

# Check if service is running
sleep 3
if sudo systemctl is-active --quiet fastapi; then
    echo "✅ FastAPI service started successfully!"
else
    echo "❌ FastAPI service failed to start. Checking logs..."
    sudo journalctl -u fastapi --no-pager -l
fi

echo ""
echo "🎉 Minimal deployment completed!"
echo ""
echo "📋 Service commands:"
echo "  Start:   sudo systemctl start fastapi"
echo "  Stop:    sudo systemctl stop fastapi"
echo "  Status:  sudo systemctl status fastapi"
echo "  Logs:    sudo journalctl -u fastapi -f"
echo ""
echo "🔗 Your API is available at:"
echo "  http://$(curl -s ifconfig.me):80"
echo "  http://$(curl -s ifconfig.me)/docs"
echo ""
echo "💡 To update: cd $APP_DIR/user-management-backend && git pull && sudo systemctl restart fastapi"