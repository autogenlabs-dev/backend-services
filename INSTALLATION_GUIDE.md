# 🚀 Autogen Backend Installation Guide

## 📋 Prerequisites

Before installing the Autogen Backend, ensure you have:

- **Python 3.8+** installed
- **PostgreSQL** (optional, can use SQLite for development)
- **Redis** (optional, for caching)
- **Git** (for cloning)

## 🔧 Installation Steps

### 1. Extract the ZIP File
```powershell
# Navigate to your desired directory
cd C:\your\desired\path

# Extract the zip file (if not already extracted)
Expand-Archive -Path "Autogen-backend.zip" -DestinationPath "autogen-backend"
cd autogen-backend
```

### 2. Create Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# If execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies
```powershell
# Navigate to the backend directory
cd user-management-backend

# Install requirements
pip install -r requirements.txt

# Or install using setup.py from root
cd ..
pip install -e .
```

### 4. Environment Configuration
```powershell
# Copy environment template
cd user-management-backend
copy .env.example .env

# Edit the .env file with your settings
notepad .env
```

### 5. Configure Environment Variables
Edit the `.env` file with your settings:

```env
# Database Configuration
DATABASE_URL=sqlite:///./test.db
# For PostgreSQL: postgresql://username:password@localhost:5432/autogen_db

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth Providers
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# LLM Provider API Keys
OPENROUTER_API_KEY=your_openrouter_api_key
GLAMA_API_KEY=your_glama_api_key
REQUESTY_API_KEY=your_requesty_api_key
AIML_API_KEY=your_aiml_api_key

# AIML OAuth (if using OAuth)
AIML_CLIENT_ID=your_aiml_client_id
AIML_CLIENT_SECRET=your_aiml_client_secret

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# App Configuration
APP_NAME=Autogen Backend
DEBUG=true
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### 6. Initialize Database
```powershell
# Initialize the database
python init_db.py

# Or run migrations if using Alembic
alembic upgrade head
```

### 7. Run the Application
```powershell
# Development server
python run_server.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 Verify Installation

### Test the API
```powershell
# Test health endpoint
curl http://localhost:8000/health

# View API documentation
# Open browser to: http://localhost:8000/docs
```

### Run Tests
```powershell
# Run all tests
pytest

# Run specific test
python test_aiml_integration.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Virtual Environment Activation Error**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Database Connection Error**
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL is running (if using PostgreSQL)
   - For SQLite, ensure write permissions

3. **Redis Connection Error**
   - Install Redis: `choco install redis-64` (if using Chocolatey)
   - Or disable Redis in config

4. **Port Already in Use**
   ```powershell
   # Find process using port 8000
   netstat -ano | findstr :8000
   
   # Kill the process (replace PID)
   taskkill /PID <PID> /F
   ```

## 📚 Next Steps

1. **Configure OAuth Providers**: Set up GitHub, Google, and AIML OAuth applications
2. **Set up Stripe**: Configure payment processing
3. **Configure LLM APIs**: Add your API keys for OpenRouter, Glama, Requesty, and AIML
4. **Deploy**: Follow production deployment guide

## 🔗 Useful URLs

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📞 Support

For issues or questions:
- Check the AIML_INTEGRATION_GUIDE.md
- Review API_INTEGRATION_GUIDE.md
- Check TESTING_SUMMARY.md for test examples
