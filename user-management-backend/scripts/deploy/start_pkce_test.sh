#!/bin/bash
# Quick Start Guide for PKCE OAuth Implementation

echo "═══════════════════════════════════════════════════════════════"
echo "  PKCE OAuth Implementation - Quick Start Guide"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if Redis is running
echo "📦 Step 1: Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "⚠️  Redis is not running. Starting Redis..."
    echo "   Option 1: docker run -d -p 6379:6379 redis:latest"
    echo "   Option 2: redis-server &"
    echo ""
    echo "Please start Redis and run this script again."
    exit 1
fi

# Check if backend is running
echo ""
echo "🚀 Step 2: Checking Backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
    echo ""
    echo "⚠️  IMPORTANT: You need to restart the backend to load new endpoints!"
    echo ""
    echo "To restart the backend:"
    echo "  1. Find the process: ps aux | grep uvicorn"
    echo "  2. Kill it: kill <PID>"
    echo "  3. Start again: python -m uvicorn app.main:app --reload"
    echo ""
else
    echo "⚠️  Backend is not running"
    echo ""
    echo "To start the backend:"
    echo "  cd /home/cis/Downloads/backend-services/user-management-backend"
    echo "  python -m uvicorn app.main:app --reload"
    echo ""
    exit 1
fi

# Run tests
echo "🧪 Step 3: Running PKCE Flow Tests..."
echo ""
python3 test_pkce_flow.py

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Next Steps"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Restart the backend server to load new endpoints"
echo "2. Verify endpoints at: http://localhost:8000/docs"
echo "3. Look for: POST /api/auth/token"
echo "4. Test with: python3 test_pkce_flow.py"
echo "5. Integrate with VS Code extension per authdoc.md"
echo ""
echo "📖 Full documentation: PKCE_IMPLEMENTATION_COMPLETE.md"
echo ""
