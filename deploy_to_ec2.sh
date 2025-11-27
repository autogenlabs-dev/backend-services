#!/bin/bash

# Deploy updated backend to EC2 and fix CORS
# Your EC2: ubuntu@ip-172-31-42-58
# Frontend: codemurf.com
# Backend: api.codemurf.com

set -e  # Exit on error

EC2_HOST="ubuntu@ip-172-31-42-58"
BACKEND_PATH="/home/ubuntu/backend-services/user-management-backend"  # Adjust if different

echo "========================================="
echo "🚀 Deploying CORS Fix to EC2"
echo "========================================="
echo "EC2 Host: $EC2_HOST"
echo "Backend Domain: api.codemurf.com"
echo "Frontend Domain: codemurf.com"
echo "========================================="
echo ""

# Step 1: Push local changes to git
echo "📦 Step 1: Committing and pushing local changes..."
git add user-management-backend/app/main.py
git commit -m "Fix CORS configuration for production deployment" || echo "No changes to commit"
git push origin main
echo "✅ Code pushed to repository"
echo ""

# Step 2: SSH to EC2 and update
echo "🔄 Step 2: SSHing to EC2 and pulling latest code..."
ssh $EC2_HOST << 'ENDSSH'
    echo "📍 Connected to EC2"
    
    # Navigate to backend directory
    cd /home/ubuntu/backend-services/user-management-backend || exit 1
    
    # Pull latest code
    echo "📥 Pulling latest code from git..."
    git pull origin main
    
    # Check if virtual environment exists
    if [ -d ".venv" ]; then
        echo "🐍 Activating virtual environment..."
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        echo "🐍 Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Install any new dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt --quiet
    
    # Check current process
    echo "🔍 Checking backend process..."
    ps aux | grep uvicorn | grep -v grep || echo "No uvicorn process found"
    
    echo ""
    echo "✅ Code updated on EC2!"
    echo ""
    echo "Next: Restart your backend service"
ENDSSH

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "Now restart your backend on EC2:"
echo ""
echo "Choose the method you use:"
echo ""
echo "1️⃣  If using PM2:"
echo "   ssh $EC2_HOST"
echo "   pm2 restart backend"
echo "   pm2 logs backend"
echo ""
echo "2️⃣  If using systemd:"
echo "   ssh $EC2_HOST"
echo "   sudo systemctl restart user-management-backend"
echo "   sudo systemctl status user-management-backend"
echo ""
echo "3️⃣  If running directly:"
echo "   ssh $EC2_HOST"
echo "   pkill -f uvicorn"
echo "   cd /home/ubuntu/backend-services/user-management-backend"
echo "   nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &"
echo ""
echo "4️⃣  If using Docker:"
echo "   ssh $EC2_HOST"
echo "   docker-compose restart backend"
echo ""
echo "========================================="
