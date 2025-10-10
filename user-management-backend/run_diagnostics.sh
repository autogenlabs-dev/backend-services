#!/bin/bash
# Quick diagnostic script to run on EC2 server

echo "🔍 Diagnosing Account Issues on EC2 Server"
echo "========================================"
echo ""

# Check if inside docker container or host
if [ -f /.dockerenv ]; then
    echo "📦 Running inside Docker container"
    python3 diagnose_accounts.py
else
    echo "💻 Running on host system"
    echo ""
    echo "Option 1: Run diagnostic inside container"
    echo "docker exec -it user-management-backend-api-1 python3 diagnose_accounts.py"
    echo ""
    echo "Option 2: Run diagnostic on host (will connect to mongodb://localhost:27017)"
    
    # Check if we have the script
    if [ -f "diagnose_accounts.py" ]; then
        echo ""
        echo "Running diagnostic from host..."
        python3 diagnose_accounts.py
    else
        echo ""
        echo "❌ diagnose_accounts.py not found. Please pull latest code:"
        echo "   git pull origin main"
    fi
fi
