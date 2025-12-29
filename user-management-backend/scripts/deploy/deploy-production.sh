#!/bin/bash

# Production Deployment Script for User Management Backend
echo "🚀 Starting production deployment..."

# Set production environment
export ENVIRONMENT=production

# Load production environment variables
if [ -f .env.production ]; then
    echo "📄 Loading production environment variables..."
    export $(cat .env.production | grep -v '#' | awk '/=/ {print $1}')
else
    echo "❌ .env.production file not found!"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Start the application
echo "🌟 Starting production server on port ${PORT:-8000}..."
uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --workers 4

echo "✅ Production deployment completed!"
