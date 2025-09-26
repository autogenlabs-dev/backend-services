#!/bin/bash
# EC2 Deployment Script for FastAPI Backend
# Run this on your EC2 instance to set up the application

set -e  # Exit on any error

echo "🚀 Starting FastAPI Backend Deployment on EC2..."

# Update system packages
sudo apt update
sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    pkg-config \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    nginx \
    redis-server

# Install MongoDB (if needed)
echo "📦 Installing MongoDB..."
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start and enable services
sudo systemctl start mongod
sudo systemctl enable mongod
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create application directory
APP_DIR="/opt/backend-services"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone repository (if not already present)
if [ ! -d "$APP_DIR/.git" ]; then
    cd /opt
    sudo git clone https://github.com/autogenlabs-dev/backend-services.git
    sudo chown -R $USER:$USER $APP_DIR
fi

cd $APP_DIR/user-management-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create environment file template
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=mongodb://localhost:27017/user_management_db
MONGODB_URL=mongodb://localhost:27017/user_management_db

# Redis Configuration
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# API Configuration
API_BASE_URL=http://localhost:8000
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# AWS Configuration (if needed)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# Stripe Configuration (if needed)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Email Configuration (if needed)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["*"]

# Environment
ENVIRONMENT=production
DEBUG=false
EOF
    echo "⚠️  Please edit .env file with your actual configuration values!"
fi

# Create systemd service file
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/fastapi-backend.service > /dev/null << EOF
[Unit]
Description=FastAPI Backend Service
After=network.target mongod.service redis-server.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR/user-management-backend
Environment=PATH=$APP_DIR/user-management-backend/venv/bin
ExecStart=$APP_DIR/user-management-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
echo "🌐 Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/fastapi-backend > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/fastapi-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable fastapi-backend

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration: nano $APP_DIR/user-management-backend/.env"
echo "2. Update nginx server_name: sudo nano /etc/nginx/sites-available/fastapi-backend"
echo "3. Start the service: sudo systemctl start fastapi-backend"
echo "4. Check service status: sudo systemctl status fastapi-backend"
echo "5. View logs: sudo journalctl -u fastapi-backend -f"
echo ""
echo "🔗 Your API will be available at:"
echo "- Local: http://localhost:8000"
echo "- Public: http://your-ec2-public-ip"
echo "- API Docs: http://your-ec2-public-ip/docs"