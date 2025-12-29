#!/bin/bash
# Reset the database that the Docker API container is actually using

echo "🔄 RESETTING DATABASE INSIDE DOCKER CONTAINER"
echo "========================================"
echo ""
echo "This will reset the database that the API container is connected to"
echo "and create fresh accounts with SHA-256 password hashes."
echo ""

# Check if container is running
if ! docker ps | grep -q "user-management-backend-api-1"; then
    echo "❌ API container is not running!"
    echo "Start it with: docker-compose up -d"
    exit 1
fi

echo "✅ API container is running"
echo ""
echo "📋 Running reset script INSIDE the container..."
echo "   This ensures we reset the correct database."
echo ""

# Copy the reset script into the container if needed
docker exec user-management-backend-api-1 ls reset_live_db.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "📦 Copying reset script to container..."
    docker cp reset_live_db.py user-management-backend-api-1:/app/reset_live_db.py
fi

# Run the reset script inside the container
echo "🚀 Executing database reset..."
echo ""
docker exec -it user-management-backend-api-1 python3 /app/reset_live_db.py --confirm

echo ""
echo "========================================"
echo "✅ Database reset complete!"
echo ""
echo "🔐 Login credentials:"
echo "   👑 superadmin@codemurf.com / SuperAdmin2025!@#"
echo "   🛡️  admin@codemurf.com / Admin2025!@#"
echo "   💻 dev1@codemurf.com / Dev1Pass2025!"
echo "   💻 dev2@codemurf.com / Dev2Pass2025!"
echo ""
echo "🧪 Test login now - the 'Invalid salt' error should be fixed!"
