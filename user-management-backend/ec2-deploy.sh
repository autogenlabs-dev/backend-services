#!/bin/bash

# EC2 Production Deployment Script
echo "🚀 Starting EC2 production deployment for User Management Backend..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing required packages..."
sudo apt install -y python3-pip python3-venv nginx redis-server git

# Navigate to project directory
cd ~/backend-services/user-management-backend

# Create and activate virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Copy production environment file
echo "📄 Setting up production environment..."
cp .env.production .env

# Set environment variables
export ENVIRONMENT=production
export $(cat .env | grep -v '#' | awk '/=/ {print $1}')

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Start Redis service
echo "🔴 Starting Redis service..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create systemd service for the application
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/user-management-backend.service > /dev/null <<EOF
[Unit]
Description=User Management Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/backend-services/user-management-backend
Environment=PATH=/home/ubuntu/backend-services/user-management-backend/venv/bin
EnvironmentFile=/home/ubuntu/backend-services/user-management-backend/.env
ExecStart=/home/ubuntu/backend-services/user-management-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start the service
echo "🌟 Starting the application service..."
sudo systemctl daemon-reload
sudo systemctl enable user-management-backend
sudo systemctl start user-management-backend

# Configure Nginx as reverse proxy
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/user-management-backend > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/user-management-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Enable firewall rules
echo "🔥 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Check service status
echo "✅ Checking service status..."
sudo systemctl status user-management-backend --no-pager
sudo systemctl status nginx --no-pager
sudo systemctl status redis-server --no-pager

echo "🎉 EC2 production deployment completed!"
echo "🌐 Your application should be accessible at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "📋 Useful commands:"
echo "  - Check logs: sudo journalctl -u user-management-backend -f"
echo "  - Restart service: sudo systemctl restart user-management-backend"
echo "  - Check status: sudo systemctl status user-management-backend"
