#!/bin/bash
# Database Connection Troubleshooting for EC2

echo "🔍 Database Connection Troubleshooting"
echo "====================================="

echo ""
echo "📋 Checking current directory and files..."
pwd
ls -la

echo ""
echo "🔍 Looking for .env files..."
if [ -f ".env" ]; then
    echo "✅ Found .env file"
    echo "DATABASE_URL setting:"
    grep "DATABASE_URL" .env || echo "❌ No DATABASE_URL found in .env"
else
    echo "❌ No .env file found"
fi

if [ -f ".env.production" ]; then
    echo "✅ Found .env.production file"
    echo "DATABASE_URL setting:"
    grep "DATABASE_URL" .env.production || echo "❌ No DATABASE_URL found in .env.production"
else
    echo "❌ No .env.production file found"
fi

echo ""
echo "🔍 Checking app/config.py..."
if [ -f "app/config.py" ]; then
    echo "✅ Found app/config.py"
    echo "Configuration preview:"
    head -20 app/config.py
else
    echo "❌ No app/config.py found"
fi

echo ""
echo "🔧 Testing MongoDB connection manually..."
python3 -c "
import os
from dotenv import load_dotenv

# Try to load environment variables
load_dotenv()

database_url = os.getenv('DATABASE_URL')
if database_url:
    print(f'✅ DATABASE_URL found: {database_url[:50]}...')
    
    # Check if it's a proper MongoDB Atlas URL
    if 'mongodb+srv://' in database_url:
        print('✅ MongoDB Atlas URL format detected')
    elif 'mongodb://' in database_url and 'localhost' in database_url:
        print('⚠️  Local MongoDB URL detected - this won\\'t work on EC2')
    else:
        print('❓ Unknown database URL format')
else:
    print('❌ No DATABASE_URL environment variable found')
"

echo ""
echo "💡 Solutions:"
echo "1. Create/update .env file with production MongoDB Atlas URL"
echo "2. Or set environment variable: export DATABASE_URL='mongodb+srv://...'"
echo "3. Check if .env.production exists and rename to .env"