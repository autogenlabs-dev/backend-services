#!/bin/bash
# Simple Python Dependencies Installation for EC2
# Use this if you just want to install the Python packages

set -e

echo "🐍 Installing Python dependencies for FastAPI Backend..."

# Update system python packages
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev build-essential libpq-dev

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

echo "✅ Python dependencies installed successfully!"
echo "💡 To activate the virtual environment: source venv/bin/activate"
echo "🚀 To run the server: uvicorn app.main:app --host 0.0.0.0 --port 8000"