#!/bin/bash

# CORS Testing Script for EC2 Production Backend
# Usage: ./test_cors.sh [BACKEND_URL] [FRONTEND_ORIGIN]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values (change these to your actual URLs)
BACKEND_URL="${1:-http://localhost:8000}"
FRONTEND_ORIGIN="${2:-http://localhost:3000}"

echo "========================================="
echo "🧪 CORS Testing Script"
echo "========================================="
echo "Backend URL: $BACKEND_URL"
echo "Frontend Origin: $FRONTEND_ORIGIN"
echo "========================================="
echo ""

# Test 1: Health Check
echo "📍 Test 1: Backend Health Check"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
    echo "   Response: $RESPONSE_BODY"
else
    echo -e "${RED}❌ Backend health check failed (HTTP $HTTP_CODE)${NC}"
    exit 1
fi
echo ""

# Test 2: OPTIONS preflight request for /api/templates
echo "📍 Test 2: CORS Preflight Request (OPTIONS)"
CORS_RESPONSE=$(curl -s -I -X OPTIONS \
  -H "Origin: $FRONTEND_ORIGIN" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  "$BACKEND_URL/api/templates")

echo "$CORS_RESPONSE"
echo ""

# Check for CORS headers
if echo "$CORS_RESPONSE" | grep -qi "access-control-allow-origin"; then
    ALLOWED_ORIGIN=$(echo "$CORS_RESPONSE" | grep -i "access-control-allow-origin" | cut -d' ' -f2 | tr -d '\r')
    
    if [ "$ALLOWED_ORIGIN" = "$FRONTEND_ORIGIN" ] || [ "$ALLOWED_ORIGIN" = "*" ]; then
        echo -e "${GREEN}✅ CORS is properly configured${NC}"
        echo "   Allowed Origin: $ALLOWED_ORIGIN"
    else
        echo -e "${YELLOW}⚠️  CORS header present but origin mismatch${NC}"
        echo "   Expected: $FRONTEND_ORIGIN"
        echo "   Got: $ALLOWED_ORIGIN"
    fi
else
    echo -e "${RED}❌ CORS headers NOT found${NC}"
    echo -e "${RED}   Your backend is not allowing requests from: $FRONTEND_ORIGIN${NC}"
    echo ""
    echo "Fix: Add the following to your EC2 environment:"
    echo "  export CORS_EXTRA_ORIGINS=\"$FRONTEND_ORIGIN\""
    echo ""
    exit 1
fi
echo ""

# Test 3: Actual GET request to /api/templates
echo "📍 Test 3: GET Request to /api/templates"
TEMPLATES_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Origin: $FRONTEND_ORIGIN" \
  "$BACKEND_URL/api/templates")

HTTP_CODE=$(echo "$TEMPLATES_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$TEMPLATES_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Templates API is accessible${NC}"
    echo "   HTTP Status: $HTTP_CODE"
else
    echo -e "${RED}❌ Templates API request failed (HTTP $HTTP_CODE)${NC}"
    echo "   Response: $RESPONSE_BODY"
fi
echo ""

# Test 4: Check /api/components
echo "📍 Test 4: GET Request to /api/components"
COMPONENTS_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Origin: $FRONTEND_ORIGIN" \
  "$BACKEND_URL/api/components")

HTTP_CODE=$(echo "$COMPONENTS_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$COMPONENTS_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Components API is accessible${NC}"
    echo "   HTTP Status: $HTTP_CODE"
else
    echo -e "${RED}❌ Components API request failed (HTTP $HTTP_CODE)${NC}"
    echo "   Response: $RESPONSE_BODY"
fi
echo ""

# Summary
echo "========================================="
echo "📊 Test Summary"
echo "========================================="
echo ""
echo "If all tests passed, CORS is configured correctly!"
echo ""
echo "If tests failed, add your frontend origin to EC2:"
echo "  1. SSH to EC2: ssh -i your-key.pem ec2-user@your-ip"
echo "  2. Add: export CORS_EXTRA_ORIGINS=\"$FRONTEND_ORIGIN\""
echo "  3. Restart backend"
echo ""
echo "See EC2_CORS_FIX_GUIDE.md for detailed instructions"
echo "========================================="
