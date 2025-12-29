#!/bin/bash
# Test component creation with real authentication token

echo "🧪 Testing Component Creation API with Authentication"
echo "====================================================="
echo ""

TOKEN='eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18zNVFUNnhGTnZDM2daOG5zZ0VoU0tRaGdxR2siLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwczovL3d3dy5jb2RlbXVyZi5jb20iLCJleHAiOjE3NjQ1ODA5ODgsImZ2YSI6WzExLC0xXSwiaWF0IjoxNzY0NTgwOTI4LCJpc3MiOiJodHRwczovL2NsZXJrLmNvZGVtdXJmLmNvbSIsIm5iZiI6MTc2NDU4MDkxOCwibyI6eyJpZCI6Im9yZ18zNWtUdnBMOVN6VjFKQmd2dzlQUUR3YXRJTlgiLCJyb2wiOiJhZG1pbiIsInNsZyI6ImNvZGVtdXJmLTE3NjM2NTMzMDIifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJzaWQiOiJzZXNzXzM2RW1oSTg1RHdWS0VZeEkySWszbm1RaG9oNiIsInN0cyI6ImFjdGl2ZSIsInN1YiI6InVzZXJfMzVrVHVtM0VTUkw0ZWRlaWxTTUJsSG5CVUo4IiwidiI6Mn0.CWbcPiwXwiPQjdWlgRn_h-Kf3O_KV-txlIaY7dlVmSw0q44Dn3Vf2HkQcXxzGkzs1RF9SS-NdAWqnuBgRv36WjN5CS9KmGwa6-wX4txQvbB5nGgVEfKrnzxq5mjvI7dV9Pnxcb-yJ5cODm6phnUYGMnOFRxnn4VUFT1CLaugK6VnK7FHAaJ_zit-y8ekowYTG886ZkfyjZPmDSQory_Dck7eYQDYNLT415u205Z-VUY4GPXwRmbvq-OxkDSDJ8mt6MeAQeb3I_ism7Lwz8LVFJzReB_mDR2w5dHfDsHHLQDeb5eQYFncVFl24ZsWjcCq_8qMk6Dh8Cc2phPoRCBEXQ'

echo "📝 Creating test component..."
echo ""

# Create component with trailing slash in URL
RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/components/' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "title": "Test Button Auth",
    "category": "User Interface",
    "type": "button",
    "language": "HTML/Tailwind",
    "difficulty_level": "Beginner",
    "plan_type": "Free",
    "short_description": "test component with auth",
    "full_description": "",
    "preview_images": [],
    "dependencies": [],
    "tags": ["test"],
    "developer_name": "Test Dev",
    "developer_experience": "Junior",
    "is_available_for_dev": true,
    "featured": false,
    "code": "<button class=\"btn\">Click Me</button>",
    "readme_content": null
  }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Check if successful
SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
COMPONENT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('component', {}).get('id', ''))" 2>/dev/null)

if [ "$SUCCESS" = "True" ] && [ -n "$COMPONENT_ID" ]; then
    echo "✅ Component created successfully with ID: $COMPONENT_ID"
    echo ""
    echo "📊 Checking database..."
    docker exec user-management-backend-mongodb-1 mongosh --quiet --eval "use codemurf; print('Total components:', db.components.countDocuments({})); db.components.find({}, {title: 1, _id: 1}).forEach(c => print('- ' + c.title + ' [' + c._id + ']'))"
else
    echo "❌ Component creation failed or returned unexpected response"
fi
