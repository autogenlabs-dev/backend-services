#!/bin/bash
# Minimal Python Dependencies Installation for EC2
# No system packages, just Python virtual environment

set -e

echo "🐍 Installing minimal Python dependencies..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found in current directory"
    echo "Please run this script from the user-management-backend directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies without cache to save space
echo "📦 Installing Python packages (no cache)..."
pip install --no-cache-dir -r requirements.txt

# Verify installation
echo "✅ Verifying installation..."
python -c "import fastapi, uvicorn, beanie; print('Core packages installed successfully!')"

echo ""
echo "✅ Minimal Python dependencies installed successfully!"
echo ""
echo "🚀 To run the server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "📊 Installed packages:"
pip list --format=freeze | wc -l | xargs echo "Total packages:"