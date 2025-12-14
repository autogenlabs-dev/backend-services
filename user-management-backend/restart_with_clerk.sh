#!/bin/bash

# Clerk Authentication - Docker Restart Script
# This script restarts the Docker containers with updated Clerk configuration

echo "🔄 Clerk Authentication Setup - Restarting Docker Containers"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

echo -e "${YELLOW}Step 1: Stopping existing containers...${NC}"
docker-compose down

echo ""
echo -e "${YELLOW}Step 2: Removing old images (optional)...${NC}"
read -p "Do you want to remove old images? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose rm -f
    echo -e "${GREEN}✅ Old containers removed${NC}"
fi

echo ""
echo -e "${YELLOW}Step 3: Rebuilding containers with new configuration...${NC}"
docker-compose build --no-cache api

echo ""
echo -e "${YELLOW}Step 4: Starting containers...${NC}"
docker-compose up -d

echo ""
echo -e "${YELLOW}Step 5: Waiting for services to be ready...${NC}"
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers are running${NC}"
else
    echo -e "${RED}❌ Containers failed to start${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 6: Verifying environment variables...${NC}"
docker-compose exec -T api env | grep CLERK

echo ""
echo -e "${YELLOW}Step 7: Testing health endpoint...${NC}"
sleep 3
curl -s http://localhost:8000/health | grep -q "ok" && echo -e "${GREEN}✅ Backend is healthy${NC}" || echo -e "${RED}❌ Backend health check failed${NC}"

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "Next steps:"
echo "1. View logs: docker-compose logs -f api"
echo "2. Run diagnostic test: python test_clerk_auth_flow.py"
echo "3. Test with frontend at http://localhost:3000"
echo ""
echo "Troubleshooting:"
echo "- Check logs: docker-compose logs api"
echo "- Restart: docker-compose restart api"
echo "- Shell access: docker-compose exec api bash"
echo ""
