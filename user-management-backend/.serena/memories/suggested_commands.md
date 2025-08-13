# Development Commands and Workflows

## Essential Commands for Windows Development

### Server Management
```bash
# Start the main application server
python minimal_auth_server.py

# Start with auto-reload (development)
uvicorn minimal_auth_server:app --reload --host 0.0.0.0 --port 8000

# Background server start
python minimal_auth_server.py &
```

### Testing Commands
```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python test_admin_dashboard.py
python test_enhanced_models.py
python test_registration_login.py

# Quick verification of Phase 2 implementation
python verify_phase2.py

# Test specific endpoints
python check_endpoints.py
python test_template_apis.py
```

### Database Management
```bash
# Initialize MongoDB collections
python init_mongodb.py

# Initialize template database
python init_template_db.py

# Reset template database
python reset_template_db.py

# Seed templates with test data
python seed_templates.py
```

### Development Utilities
```bash
# Check user data
python check_users.py

# Check templates
python check_templates.py

# Get API specification
python get_api_spec.py

# Quick login testing
python quick_login_test.py
```

### Windows System Commands
```bash
# Directory listing
dir
ls  # if using PowerShell or Git Bash

# Change directory
cd path\to\directory

# Find files
where filename
findstr /s "pattern" *.py

# Process management
tasklist | findstr python
taskkill /f /pid PROCESS_ID
```

### Docker Operations
```bash
# Build and run with Docker
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Deployment Commands
```bash
# Deploy to server (PowerShell)
.\deploy.ps1

# Deploy to server (Bash)
bash deploy.sh

# EC2 setup
bash ec2-setup.sh
```

### Git Workflow
```bash
# Standard Git operations
git status
git add .
git commit -m "message"
git push origin main

# Branch management
git checkout -b feature/new-feature
git merge feature/new-feature
```

### Python Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Check installed packages
pip list
pip freeze > requirements.txt
```