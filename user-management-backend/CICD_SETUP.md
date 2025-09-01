# GitHub Secrets Setup Guide

To set up the CI/CD pipeline, you need to configure the following secrets in your GitHub repository:

## 🔐 Required GitHub Secrets

Go to your GitHub repository: `Settings > Secrets and variables > Actions > New repository secret`

### 1. EC2 Connection Secrets

**EC2_HOST**
```
your-ec2-public-ip-or-domain
```

**EC2_USER** 
```
ubuntu
```

**EC2_SSH_PRIVATE_KEY**
```
-----BEGIN OPENSSH PRIVATE KEY-----
[Your private key content here]
-----END OPENSSH PRIVATE KEY-----
```

### 2. Production Environment File (PRODUCTION_ENV_FILE)

Create a secret named `PRODUCTION_ENV_FILE` with the complete content of your `.env.production` file:

```bash
# Production Environment Configuration
DATABASE_URL=mongodb+srv://autogencodebuilder:DataOnline@autogen.jf0j0.mongodb.net/user_management_db_prod?retryWrites=true&w=majority&connectTimeoutMS=60000&socketTimeoutMS=60000
REDIS_URL=redis://localhost:6379

# Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production

# JWT Configuration
JWT_SECRET_KEY=pYi91CEGA63x9-d8HtfyPk1YgFZ8nDruadSfSESkF88
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe Configuration (Production Keys)
STRIPE_SECRET_KEY=sk_live_REPLACE_WITH_YOUR_LIVE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_live_REPLACE_WITH_YOUR_LIVE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=whsec_REPLACE_WITH_YOUR_LIVE_WEBHOOK_SECRET

# Razorpay Configuration (Production credentials)
RAZORPAY_KEY_ID=rzp_live_REPLACE_WITH_YOUR_LIVE_KEY_ID
RAZORPAY_KEY_SECRET=REPLACE_WITH_YOUR_LIVE_SECRET_KEY

# Application Configuration
APP_NAME=User Management Backend
DEBUG=False
API_V1_STR=/api
PROJECT_NAME=User Management API

# CORS Configuration
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# OAuth Providers
OAUTH_PROVIDERS=["openrouter", "glama", "requesty", "aiml"]

# LLM Provider API Keys
OPENROUTER_API_KEY=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
GLAMA_API_KEY=your_production_glama_api_key
REQUESTY_API_KEY=sk-mgH1Qvc+RL294Gzwu/J3fEkuQDK8GdjOduYfZa5QX6ExBj/3N/XK6kBjlyMwljIdBAbgfZhEIb2RiE+UeceAT0ucBVIl1ZHNf+32PpQJegQ=
AIML_API_KEY=your_production_aiml_api_key

# A4F API Key for VS Code Extension
A4F_API_KEY=ddc-a4f-a480842d898b49d4a15e14800c2f3c72
A4F_BASE_URL=https://api.a4f.co/v1

# Rate Limiting
DEFAULT_RATE_LIMIT_PER_MINUTE=60
PRO_RATE_LIMIT_PER_MINUTE=300
ENTERPRISE_RATE_LIMIT_PER_MINUTE=1000

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_URL=redis://localhost:6379
```

## 📝 How to Set Up SSH Key

1. On your local machine, generate SSH key (if you don't have one):
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

2. Copy the public key to your EC2 instance:
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@your-ec2-ip
```

3. Copy the PRIVATE key content and add it to GitHub secrets as `EC2_SSH_PRIVATE_KEY`:
```bash
cat ~/.ssh/id_rsa
```

## 🚀 Deployment Workflows

I've created two deployment options:

### Option 1: Direct Deployment (deploy.yml)
- Runs tests
- Deploys directly via SSH
- Uses systemd service
- Includes rollback mechanism

### Option 2: Docker Deployment (docker-deploy.yml)
- Builds Docker image
- Pushes to GitHub Container Registry
- Deploys via Docker on EC2
- More isolated and scalable

## 🔧 Manual Setup Commands

Run these on your EC2 instance first:

```bash
# Clone your repository
git clone https://github.com/autogenlabs-dev/backend-services.git
cd backend-services/user-management-backend

# Run the setup script
chmod +x ec2-deploy.sh
./ec2-deploy.sh
```

## ✅ Testing the Pipeline

1. Commit and push changes to main branch
2. Check GitHub Actions tab in your repository
3. Monitor the deployment progress
4. Verify your application is running at http://your-ec2-ip

## 🔍 Troubleshooting

- Check GitHub Actions logs for detailed error messages
- SSH into your EC2 instance to check service status:
  ```bash
  sudo systemctl status user-management-backend
  sudo journalctl -u user-management-backend -f
  ```
- Check Nginx logs:
  ```bash
  sudo tail -f /var/log/nginx/error.log
  ```
