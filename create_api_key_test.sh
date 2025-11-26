#!/bin/bash

# Get your Clerk token from the frontend
# Replace YOUR_CLERK_TOKEN with the actual token
CLERK_TOKEN="${1:-YOUR_CLERK_TOKEN}"

echo "Creating API key with Clerk token..."
echo ""

curl -X POST http://localhost:8000/api/users/me/api-keys \
  -H "Authorization: Bearer $CLERK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First API Key",
    "expires_in_days": 365
  }' | jq .

echo ""
echo "Now check your API keys:"
echo ""

curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $CLERK_TOKEN" | jq .
