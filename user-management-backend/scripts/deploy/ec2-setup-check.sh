#!/bin/bash
# EC2 Live Database Reset Setup
# Run this script on your EC2 server to set up and execute the database reset

echo "🚀 EC2 Live Database Reset Setup"
echo "================================="

# Check current directory
echo "📍 Current directory: $(pwd)"
echo "📁 Directory contents:"
ls -la

echo ""
echo "🔍 Checking for Docker containers..."
echo "Running containers:"
docker ps

echo ""
echo "All containers (including stopped):"
docker ps -a

echo ""
echo "🔍 Checking for docker-compose..."
if [ -f "docker-compose.yml" ]; then
    echo "✅ Found docker-compose.yml"
    echo "Docker Compose services:"
    docker-compose ps
else
    echo "❌ No docker-compose.yml found"
fi

echo ""
echo "🔍 Checking for backend files..."
if [ -f "reset_live_db.py" ]; then
    echo "✅ Found reset_live_db.py"
else
    echo "❌ reset_live_db.py not found - need to create it"
fi

if [ -f "app/main.py" ]; then
    echo "✅ Found backend app structure"
else
    echo "❌ Backend app structure not found"
fi

echo ""
echo "🔍 Python environment check..."
python3 --version
pip3 list | grep -E "(motor|beanie|fastapi)" || echo "⚠️ Required packages may not be installed"

echo ""
echo "📋 Next Steps:"
echo "1. Upload reset_live_db.py script to this directory"
echo "2. Start Docker containers if needed"
echo "3. Install Python dependencies" 
echo "4. Run database reset"