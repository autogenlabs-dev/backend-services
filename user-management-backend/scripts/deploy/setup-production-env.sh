#!/bin/bash
# Production Environment Setup Script
# This script helps you create a production .env file

echo "🔧 Production Environment Setup"
echo "================================"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  Warning: .env file already exists!"
    read -p "Do you want to backup and recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv .env .env.backup.$(date +%Y%m%d_%H%M%S)
        echo "✅ Backed up existing .env"
    else
        echo "❌ Aborted"
        exit 0
    fi
fi

# Start creating .env
echo "Creating .env file..."
echo ""

# Generate JWT Secret
JWT_SECRET=$(openssl rand -hex 32)
echo "✅ Generated JWT Secret"

# Create .env file
cat > .env << 'EOF'
# ==============================================
# Production Environment Configuration
# ==============================================
# Generated on: $(date)

# ==============================================
# Application Settings
# ==============================================
DEBUG=False
ENVIRONMENT=production
APP_NAME=User Management Backend
HOST=0.0.0.0
PORT=8000

# ==============================================
# Security - JWT Configuration
# ==============================================
EOF

echo "JWT_SECRET_KEY=$JWT_SECRET" >> .env

cat >> .env << 'EOF'
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ==============================================
# Database Configuration (Docker internal)
# ==============================================
DATABASE_URL=mongodb://mongodb:27017/user_management_db
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=user_management_db
REDIS_URL=redis://redis:6379

EOF

echo ""
echo "✅ Created .env with secure JWT secret"
echo ""
echo "⚠️  You MUST manually update these values:"
echo ""
echo "1. Clerk Configuration (from dashboard.clerk.com):"
echo "   - CLERK_JWKS_URL"
echo "   - CLERK_ISSUER"
echo "   - CLERK_AUDIENCE"
echo ""
echo "2. OAuth Credentials (Google, GitHub):"
echo "   - GOOGLE_CLIENT_ID"
echo "   - GOOGLE_CLIENT_SECRET"
echo "   - GITHUB_CLIENT_ID"
echo "   - GITHUB_CLIENT_SECRET"
echo ""
echo "3. OAuth Redirect URIs (update to your domain):"
echo "   - GOOGLE_REDIRECT_URI"
echo ""

# Ask for Clerk configuration
read -p "Enter your production domain (e.g., api.yourdomain.com): " DOMAIN
if [ ! -z "$DOMAIN" ]; then
    echo ""
    read -p "Enter your Clerk instance (e.g., your-app-name): " CLERK_INSTANCE
    
    if [ ! -z "$CLERK_INSTANCE" ]; then
        cat >> .env << EOF

# ==============================================
# Clerk Authentication
# ==============================================
CLERK_JWKS_URL=https://${CLERK_INSTANCE}.clerk.accounts.dev/.well-known/jwks.json
CLERK_ISSUER=https://${CLERK_INSTANCE}.clerk.accounts.dev
CLERK_AUDIENCE=https://${DOMAIN}
CLERK_JWKS_TTL=300
CLERK_SECRET_KEY=

EOF
        echo "✅ Added Clerk configuration"
    fi
    
    cat >> .env << EOF

# ==============================================
# OAuth Providers
# ==============================================
GOOGLE_CLIENT_ID=CHANGE_ME
GOOGLE_CLIENT_SECRET=CHANGE_ME
GOOGLE_REDIRECT_URI=https://${DOMAIN}/api/auth/google/callback

GITHUB_CLIENT_ID=CHANGE_ME
GITHUB_CLIENT_SECRET=CHANGE_ME

OPENROUTER_CLIENT_ID=your-openrouter-client-id
OPENROUTER_CLIENT_SECRET=your-openrouter-client-secret

# ==============================================
# External Services
# ==============================================
A4F_API_KEY=your-a4f-api-key
A4F_BASE_URL=https://api.a4f.com/v1

# ==============================================
# Stripe (if using)
# ==============================================
STRIPE_SECRET_KEY=sk_live_CHANGE_ME
STRIPE_PUBLISHABLE_KEY=pk_live_CHANGE_ME
STRIPE_WEBHOOK_SECRET=whsec_CHANGE_ME

# ==============================================
# IMPORTANT: GLM API Keys
# ==============================================
# GLM API keys are stored PER USER in MongoDB
# Users set via: POST /api/users/me/glm-api-key?api_key=xxx
# Retrieved via: GET /api/users/me (returns glm_api_key field)
EOF
fi

echo ""
echo "✅ .env file created successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env and replace all CHANGE_ME values"
echo "2. Update CORS in app/main.py with your domain"
echo "3. Run: docker-compose -f docker-compose.production.yml up --build -d"
echo ""
echo "📋 To edit: nano .env"
echo ""
