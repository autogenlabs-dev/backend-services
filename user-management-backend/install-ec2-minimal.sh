#!/bin/bash
# Ultra-minimal EC2 installation script
# Only installs what's absolutely necessary

set -e

echo "🚀 Ultra-minimal FastAPI installation for EC2..."

# Only install Python 3 and git if they don't exist
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip git
else
    echo "✅ Python 3 already installed"
fi

# Clone repo if needed
if [ ! -d "backend-services" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/autogenlabs-dev/backend-services.git
fi

cd backend-services/user-management-backend

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Create minimal config
cat > .env << EOF
DATABASE_URL=mongodb://localhost:27017/user_management_db
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false
ALLOWED_ORIGINS=["*"]
EOF

echo "✅ Installation complete!"
echo ""
echo "🚀 To run the server:"
echo "  cd backend-services/user-management-backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "📝 Note: You may need to install MongoDB and Redis separately:"
echo "  sudo snap install mongodb"
echo "  sudo apt install redis-server"