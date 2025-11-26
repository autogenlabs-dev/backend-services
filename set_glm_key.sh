#!/bin/bash

# Usage: ./set_glm_key.sh YOUR_CLERK_TOKEN YOUR_GLM_API_KEY

CLERK_TOKEN="${1}"
GLM_API_KEY="${2:-YOUR_GLM_API_KEY_HERE}"

if [ -z "$CLERK_TOKEN" ]; then
  echo "Usage: $0 <CLERK_TOKEN> [GLM_API_KEY]"
  echo ""
  echo "Example:"
  echo "  $0 'eyJhbG...' 'YOUR_GLM_API_KEY_HERE'"
  exit 1
fi

echo "Setting GLM API key for user..."
echo ""

curl -X POST "http://localhost:8000/api/users/me/glm-api-key?api_key=${GLM_API_KEY}" \
  -H "Authorization: Bearer ${CLERK_TOKEN}" \
  -H "Content-Type: application/json" | jq .

echo ""
echo ""
echo "Getting user profile to verify..."
echo ""

curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer ${CLERK_TOKEN}" | jq .
