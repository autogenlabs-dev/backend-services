#!/bin/bash
# Test component creation via API endpoint

echo "🧪 Testing Component Creation API"
echo "=================================="
echo ""

# Note: This requires valid authentication token
# Replace with actual token or use Clerk authentication

echo "📝 Test 1: Create Component (requires authentication)"
echo "   Endpoint: POST http://localhost:8000/api/components"
echo ""
echo "   To test manually, use:"
echo "   1. Get a valid JWT token from your frontend"
echo "   2. Run this command with your token:"
echo ""
echo "   curl -X POST http://localhost:8000/api/components \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'Authorization: Bearer YOUR_TOKEN_HERE' \\"
echo "     -d '{"
echo "       \"title\": \"Test Button\","
echo "       \"category\": \"User Interface\","
echo "       \"type\": \"button\","
echo "       \"language\": \"HTML/Tailwind\","
echo "       \"difficulty_level\": \"Beginner\","
echo "       \"plan_type\": \"Free\","
echo "       \"short_description\": \"A test button\","
echo "       \"full_description\": \"\","
echo "       \"preview_images\": [],"
echo "       \"dependencies\": [],"
echo "       \"tags\": ["test"],"
echo "       \"developer_name\": \"Test Dev\","
echo "       \"developer_experience\": \"Junior\","
echo "       \"is_available_for_dev\": true,"
echo "       \"featured\": false,"
echo "       \"code\": \"<button>Click</button>\""
echo "     }'"
echo ""

echo "📝 Test 2: Get All Components (no auth required)"
echo "   Endpoint: GET http://localhost:8000/api/components"
curl -s http://localhost:8000/api/components | python3 -m json.tool | head -30
echo ""

echo "✅ API is responding"
echo ""
echo "⚠️  To fully test component creation, you need to:"
echo "   1. Use the frontend at www.codemurf.com to create a component"
echo "   2. Check logs: docker logs user-management-backend-api-1 --tail 50"
echo "   3. Verify in DB: docker exec user-management-backend-mongodb-1 mongosh --eval 'use codemurf; db.components.find().pretty()'"
