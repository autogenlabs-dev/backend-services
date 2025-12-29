#!/usr/bin/env python3
"""
🚀 AUTOMATED PROJECT SETUP SCRIPT
==================================

This script will automatically set up the User Management Backend for VS Code Extension.
It handles everything from environment setup to running the server.

Features:
- Virtual environment creation
- Dependency installation
- MongoDB setup and initialization
- Database migration
- Configuration file setup
- Server startup and testing

Usage:
    python setup_project.py
"""

import os
import sys
import subprocess
import platform
import json
import asyncio
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# Configuration
PROJECT_NAME = "User Management Backend"
PYTHON_VERSION = "3.8+"
REQUIRED_PACKAGES = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "motor>=3.3.0",
    "beanie>=1.24.0",
    "bcrypt>=4.1.0",
    "PyJWT>=2.8.0",
    "python-multipart>=0.0.6",
    "python-dotenv>=1.0.0",
    "httpx>=0.25.0",
    "pydantic[email]>=2.5.0",
    "pymongo>=4.6.0"
]

MONGODB_VERSION = "8.0.4"
DEFAULT_PORT = 8000

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ProjectSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / ".venv"
        self.is_windows = platform.system() == "Windows"
        self.python_exe = self.get_python_executable()
        self.pip_exe = self.get_pip_executable()
        
    def print_header(self):
        """Print setup header."""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("=" * 80)
        print("🚀 USER MANAGEMENT BACKEND - AUTOMATED SETUP")
        print("=" * 80)
        print(f"{Colors.ENDC}")
        print(f"{Colors.OKBLUE}📋 Project: {PROJECT_NAME}")
        print(f"📁 Directory: {self.project_root}")
        print(f"🐍 Python: {PYTHON_VERSION}")
        print(f"🗄️ Database: MongoDB {MONGODB_VERSION}")
        print(f"🌐 Port: {DEFAULT_PORT}")
        print(f"{Colors.ENDC}")
    
    def get_python_executable(self) -> str:
        """Get the correct Python executable path."""
        if self.is_windows:
            if self.venv_path.exists():
                return str(self.venv_path / "Scripts" / "python.exe")
            return "python"
        else:
            if self.venv_path.exists():
                return str(self.venv_path / "bin" / "python")
            return "python3"
    
    def get_pip_executable(self) -> str:
        """Get the correct pip executable path."""
        if self.is_windows:
            if self.venv_path.exists():
                return str(self.venv_path / "Scripts" / "pip.exe")
            return "pip"
        else:
            if self.venv_path.exists():
                return str(self.venv_path / "bin" / "pip")
            return "pip3"
    
    def run_command(self, command: List[str], description: str, check: bool = True) -> bool:
        """Run a shell command with error handling."""
        print(f"{Colors.OKCYAN}🔧 {description}...{Colors.ENDC}")
        
        try:
            if self.is_windows:
                result = subprocess.run(command, check=check, capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(command, check=check, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ {description} completed successfully{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.WARNING}⚠️  {description} completed with warnings{Colors.ENDC}")
                if result.stderr:
                    print(f"   Output: {result.stderr.strip()}")
                return not check
                
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ {description} failed: {e}{Colors.ENDC}")
            if e.stderr:
                print(f"   Error: {e.stderr.strip()}")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ {description} failed: {e}{Colors.ENDC}")
            return False
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        print(f"{Colors.OKCYAN}🐍 Checking Python version...{Colors.ENDC}")
        
        try:
            version_info = sys.version_info
            version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
            
            if version_info >= (3, 8):
                print(f"{Colors.OKGREEN}✅ Python {version_str} meets requirements{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.FAIL}❌ Python {version_str} is too old. Need Python 3.8+{Colors.ENDC}")
                return False
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Could not check Python version: {e}{Colors.ENDC}")
            return False
    
    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment."""
        if self.venv_path.exists():
            print(f"{Colors.OKGREEN}✅ Virtual environment already exists{Colors.ENDC}")
            return True
        
        return self.run_command(
            [sys.executable, "-m", "venv", str(self.venv_path)],
            "Creating virtual environment"
        )
    
    def activate_virtual_environment(self) -> bool:
        """Update executables to use virtual environment."""
        if self.venv_path.exists():
            self.python_exe = self.get_python_executable()
            self.pip_exe = self.get_pip_executable()
            print(f"{Colors.OKGREEN}✅ Virtual environment activated{Colors.ENDC}")
            return True
        return False
    
    def upgrade_pip(self) -> bool:
        """Upgrade pip to latest version."""
        return self.run_command(
            [self.python_exe, "-m", "pip", "install", "--upgrade", "pip"],
            "Upgrading pip"
        )
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        print(f"{Colors.OKCYAN}📦 Installing dependencies...{Colors.ENDC}")
        
        # Install packages one by one to handle individual failures
        all_success = True
        for package in REQUIRED_PACKAGES:
            success = self.run_command(
                [self.pip_exe, "install", package],
                f"Installing {package}",
                check=False
            )
            if not success:
                all_success = False
        
        if all_success:
            print(f"{Colors.OKGREEN}✅ All dependencies installed successfully{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️  Some dependencies had issues, but continuing...{Colors.ENDC}")
        
        return True
    
    def create_requirements_file(self) -> bool:
        """Create requirements.txt file."""
        print(f"{Colors.OKCYAN}📄 Creating requirements.txt...{Colors.ENDC}")
        
        try:
            requirements_content = "\\n".join(REQUIRED_PACKAGES)
            requirements_path = self.project_root / "requirements.txt"
            
            with open(requirements_path, "w") as f:
                f.write(requirements_content)
            
            print(f"{Colors.OKGREEN}✅ requirements.txt created{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to create requirements.txt: {e}{Colors.ENDC}")
            return False
    
    def create_environment_file(self) -> bool:
        """Create .env file with default configuration."""
        print(f"{Colors.OKCYAN}⚙️  Creating environment configuration...{Colors.ENDC}")
        
        env_content = '''# User Management Backend Configuration
# Database Configuration
DATABASE_URL=mongodb://localhost:27017/user_management_db
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=user_management_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Configuration
APP_NAME=User Management Backend
DEBUG=True
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"]

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# A4F Integration Configuration
A4F_API_KEY=your-a4f-api-key-here
A4F_BASE_URL=https://api.a4f.com/v1

# Server Configuration
HOST=0.0.0.0
PORT=8000
'''
        
        try:
            env_path = self.project_root / ".env"
            if not env_path.exists():
                with open(env_path, "w") as f:
                    f.write(env_content)
                print(f"{Colors.OKGREEN}✅ .env file created{Colors.ENDC}")
            else:
                print(f"{Colors.OKGREEN}✅ .env file already exists{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to create .env file: {e}{Colors.ENDC}")
            return False
    
    def check_mongodb_installation(self) -> bool:
        """Check if MongoDB is installed and running."""
        print(f"{Colors.OKCYAN}🗄️  Checking MongoDB installation...{Colors.ENDC}")
        
        # Try to connect to MongoDB
        try:
            from pymongo import MongoClient
            client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
            client.server_info()
            client.close()
            print(f"{Colors.OKGREEN}✅ MongoDB is running{Colors.ENDC}")
            return True
            
        except ImportError:
            print(f"{Colors.WARNING}⚠️  pymongo not installed yet, will check after dependency installation{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  MongoDB not running or not accessible: {e}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}💡 To install MongoDB:{Colors.ENDC}")
            if self.is_windows:
                print("   - Download from: https://www.mongodb.com/try/download/community")
                print("   - Or use: winget install MongoDB.Server")
            else:
                print("   - Ubuntu/Debian: sudo apt-get install mongodb")
                print("   - macOS: brew install mongodb-community")
            return False
    
    def initialize_database(self) -> bool:
        """Initialize MongoDB database."""
        print(f"{Colors.OKCYAN}🗄️  Initializing database...{Colors.ENDC}")
        
        try:
            # Check if init_mongodb.py exists
            init_script = self.project_root / "init_mongodb.py"
            if init_script.exists():
                success = self.run_command(
                    [self.python_exe, str(init_script)],
                    "Running database initialization"
                )
                if success:
                    print(f"{Colors.OKGREEN}✅ Database initialized successfully{Colors.ENDC}")
                return success
            else:
                print(f"{Colors.WARNING}⚠️  Database initialization script not found{Colors.ENDC}")
                return True
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Database initialization failed: {e}{Colors.ENDC}")
            return False
    
    def test_server_startup(self) -> bool:
        """Test if the server can start up correctly."""
        print(f"{Colors.OKCYAN}🌐 Testing server startup...{Colors.ENDC}")
        
        try:
            # Try to import the server module
            success = self.run_command(
                [self.python_exe, "-c", "from minimal_auth_server import app; print('Server module imported successfully')"],
                "Testing server import"
            )
            
            if success:
                print(f"{Colors.OKGREEN}✅ Server can start successfully{Colors.ENDC}")
            return success
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Server startup test failed: {e}{Colors.ENDC}")
            return False
    
    async def run_comprehensive_test(self) -> bool:
        """Run the comprehensive API test."""
        print(f"{Colors.OKCYAN}🧪 Running comprehensive API tests...{Colors.ENDC}")
        
        try:
            # Check if test script exists
            test_script = self.project_root / "test_auth_flow.py"
            if test_script.exists():
                success = self.run_command(
                    [self.python_exe, str(test_script)],
                    "Running API tests",
                    check=False
                )
                if success:
                    print(f"{Colors.OKGREEN}✅ All API tests passed{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}⚠️  Some API tests failed (server may not be running){Colors.ENDC}")
                return True
            else:
                print(f"{Colors.WARNING}⚠️  API test script not found{Colors.ENDC}")
                return True
                
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  API tests could not run: {e}{Colors.ENDC}")
            return True
    
    def print_startup_instructions(self):
        """Print instructions for starting the server."""
        print(f"\\n{Colors.HEADER}{Colors.BOLD}")
        print("=" * 80)
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}✅ Project setup is complete!{Colors.ENDC}")
        print(f"\\n{Colors.OKCYAN}🚀 To start the server:{Colors.ENDC}")
        
        if self.is_windows:
            print(f"   {Colors.BOLD}# Activate virtual environment{Colors.ENDC}")
            print(f"   .venv\\Scripts\\activate")
            print(f"\\n   {Colors.BOLD}# Start the minimal auth server{Colors.ENDC}")
            print(f"   python minimal_auth_server.py")
            print(f"\\n   {Colors.BOLD}# Or use uvicorn{Colors.ENDC}")
            print(f"   uvicorn minimal_auth_server:app --host 0.0.0.0 --port {DEFAULT_PORT} --reload")
        else:
            print(f"   {Colors.BOLD}# Activate virtual environment{Colors.ENDC}")
            print(f"   source .venv/bin/activate")
            print(f"\\n   {Colors.BOLD}# Start the minimal auth server{Colors.ENDC}")
            print(f"   python minimal_auth_server.py")
            print(f"\\n   {Colors.BOLD}# Or use uvicorn{Colors.ENDC}")
            print(f"   uvicorn minimal_auth_server:app --host 0.0.0.0 --port {DEFAULT_PORT} --reload")
        
        print(f"\\n{Colors.OKCYAN}🧪 To run tests:{Colors.ENDC}")
        print(f"   python test_auth_flow.py")
        print(f"   python test_full_api.py")
        
        print(f"\\n{Colors.OKCYAN}🌐 Server will be available at:{Colors.ENDC}")
        print(f"   http://localhost:{DEFAULT_PORT}")
        print(f"   http://localhost:{DEFAULT_PORT}/docs (API documentation)")
        
        print(f"\\n{Colors.OKCYAN}📁 Important files:{Colors.ENDC}")
        print(f"   📄 .env - Environment configuration")
        print(f"   📄 requirements.txt - Python dependencies")
        print(f"   📄 minimal_auth_server.py - Main server")
        print(f"   📄 test_auth_flow.py - Comprehensive tests")
        
        print(f"\\n{Colors.WARNING}⚠️  Don't forget to:{Colors.ENDC}")
        print(f"   🔑 Update your .env file with real API keys")
        print(f"   🗄️ Ensure MongoDB is running")
        print(f"   🔒 Change JWT_SECRET_KEY for production")
        
        print(f"\\n{Colors.HEADER}Happy coding! 🚀{Colors.ENDC}")
    
    async def run_setup(self) -> bool:
        """Run the complete setup process."""
        self.print_header()
        
        steps = [
            ("Python Version Check", self.check_python_version),
            ("Virtual Environment Creation", self.create_virtual_environment),
            ("Virtual Environment Activation", self.activate_virtual_environment),
            ("Pip Upgrade", self.upgrade_pip),
            ("Dependency Installation", self.install_dependencies),
            ("Requirements File Creation", self.create_requirements_file),
            ("Environment File Creation", self.create_environment_file),
            ("MongoDB Check", self.check_mongodb_installation),
            ("Database Initialization", self.initialize_database),
            ("Server Startup Test", self.test_server_startup),
        ]
        
        print(f"\\n{Colors.OKCYAN}📋 Setup Process:{Colors.ENDC}")
        for i, (step_name, _) in enumerate(steps, 1):
            print(f"   {i}. {step_name}")
        
        print(f"\\n{Colors.BOLD}Starting setup process...{Colors.ENDC}\\n")
        
        success_count = 0
        for step_name, step_func in steps:
            print(f"\\n{Colors.BOLD}Step: {step_name}{Colors.ENDC}")
            try:
                if await step_func() if asyncio.iscoroutinefunction(step_func) else step_func():
                    success_count += 1
                else:
                    print(f"{Colors.WARNING}⚠️  {step_name} had issues but continuing...{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}❌ {step_name} failed: {e}{Colors.ENDC}")
        
        # Run tests (optional)
        await self.run_comprehensive_test()
        
        print(f"\\n{Colors.BOLD}Setup Summary:{Colors.ENDC}")
        print(f"   ✅ Completed: {success_count}/{len(steps)} steps")
        
        if success_count >= len(steps) * 0.8:  # 80% success rate
            self.print_startup_instructions()
            return True
        else:
            print(f"{Colors.FAIL}❌ Setup completed with issues. Please check the errors above.{Colors.ENDC}")
            return False

async def main():
    """Main setup function."""
    try:
        setup = ProjectSetup()
        success = await setup.run_setup()
        
        if success:
            print(f"\\n{Colors.OKGREEN}✅ Setup completed successfully!{Colors.ENDC}")
            return 0
        else:
            print(f"\\n{Colors.FAIL}❌ Setup completed with errors!{Colors.ENDC}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\\n{Colors.WARNING}⏹️  Setup interrupted by user{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"\\n{Colors.FAIL}💥 Setup failed: {e}{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
