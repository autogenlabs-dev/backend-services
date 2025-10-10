#!/bin/bash
# EC2 Dependencies Installation for Live Database Reset
# Handles both virtual environment and direct installation

echo "� Installing Python Dependencies for Database Reset"
echo "===================================================="

# Check Python version
echo "🐍 Python version:"
python3 --version

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev build-essential

# Option 1: Try installing dependencies from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    echo "📋 Found requirements.txt - installing from it..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    echo ""
    echo "✅ Dependencies installed in virtual environment!"
    echo "💡 To use: source venv/bin/activate && python3 reset_live_db.py --confirm"
    
else
    echo "📦 No requirements.txt found - installing core dependencies globally..."
    
    # Install required packages globally
    pip3 install motor beanie pydantic fastapi python-dotenv asyncio-motor pymongo dnspython
    
    echo ""
    echo "✅ Dependencies installed globally!"
    echo "💡 To use: python3 reset_live_db.py --confirm"
fi

echo ""
echo "🔍 Verifying installations..."
python3 -c "
try:
    import motor.motor_asyncio
    print('✅ motor: OK')
except ImportError as e:
    print(f'❌ motor: {e}')

try:
    import beanie
    print('✅ beanie: OK')
except ImportError as e:
    print(f'❌ beanie: {e}')

try:
    import pydantic
    print('✅ pydantic: OK')
except ImportError as e:
    print(f'❌ pydantic: {e}')

try:
    from app.config import Settings
    print('✅ app.config: OK')
except ImportError as e:
    print(f'❌ app.config: {e}')
"

echo ""
echo "🚀 Setup complete! You can now run:"
echo "python3 reset_live_db.py --confirm"
echo "🚀 To run the server: uvicorn app.main:app --host 0.0.0.0 --port 8000"