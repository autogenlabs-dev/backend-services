#!/usr/bin/env python3
"""
Quick setup script for Autogen Backend
Automates the installation and initial setup process
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and handle errors"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("\n📦 Creating virtual environment...")
    
    if os.path.exists("venv"):
        print("Virtual environment already exists")
        return True
    
    result = run_command(f"{sys.executable} -m venv venv")
    if result is None:
        return False
    
    print("✅ Virtual environment created")
    return True

def get_venv_python():
    """Get the path to Python executable in virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "python.exe")
    else:  # Unix/Linux/Mac
        return os.path.join("venv", "bin", "python")

def install_dependencies():
    """Install project dependencies"""
    print("\n📋 Installing dependencies...")
    
    venv_python = get_venv_python()
    
    # Navigate to backend directory
    backend_dir = "user-management-backend"
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    # Install requirements
    result = run_command(f"{venv_python} -m pip install --upgrade pip")
    if result is None:
        return False
    
    result = run_command(f"{venv_python} -m pip install -r {requirements_file}")
    if result is None:
        return False
    
    print("✅ Dependencies installed")
    return True

def setup_environment_file():
    """Setup environment configuration file"""
    print("\n⚙️ Setting up environment configuration...")
    
    backend_dir = "user-management-backend"
    env_example = os.path.join(backend_dir, ".env.example")
    env_file = os.path.join(backend_dir, ".env")
    
    if os.path.exists(env_file):
        print("Environment file already exists")
        return True
    
    if not os.path.exists(env_example):
        print("❌ .env.example file not found")
        return False
    
    # Copy .env.example to .env
    shutil.copy2(env_example, env_file)
    print("✅ Environment file created from template")
    print(f"📝 Please edit {env_file} with your configuration")
    return True

def initialize_database():
    """Initialize the database"""
    print("\n🗄️ Initializing database...")
    
    venv_python = get_venv_python()
    backend_dir = "user-management-backend"
    
    # Check if init_db.py exists
    init_db_script = os.path.join(backend_dir, "init_db.py")
    if os.path.exists(init_db_script):
        result = run_command(f"{venv_python} init_db.py", cwd=backend_dir)
        if result is None:
            print("❌ Database initialization failed")
            return False
    else:
        # Try alembic migration
        alembic_ini = os.path.join(backend_dir, "alembic.ini")
        if os.path.exists(alembic_ini):
            result = run_command(f"{venv_python} -m alembic upgrade head", cwd=backend_dir)
            if result is None:
                print("❌ Database migration failed")
                return False
        else:
            print("⚠️ No database initialization method found")
            print("You may need to set up the database manually")
            return True
    
    print("✅ Database initialized")
    return True

def run_tests():
    """Run basic tests to verify installation"""
    print("\n🧪 Running tests...")
    
    venv_python = get_venv_python()
    backend_dir = "user-management-backend"
    
    # Run AIML integration test
    test_file = os.path.join(backend_dir, "test_aiml_integration.py")
    if os.path.exists(test_file):
        result = run_command(f"{venv_python} test_aiml_integration.py", cwd=backend_dir, check=False)
        if result and result.returncode == 0:
            print("✅ AIML integration test passed")
        else:
            print("⚠️ AIML integration test failed (may need API keys)")
    
    print("✅ Basic tests completed")
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Edit user-management-backend/.env with your configuration")
    print("2. Add your API keys for LLM providers (OpenRouter, AIML, etc.)")
    print("3. Configure OAuth providers (GitHub, Google)")
    print("4. Set up Stripe for payments (if needed)")
    print("\n🚀 To start the server:")
    print("   cd user-management-backend")
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\Activate.ps1")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
    print("   python run_server.py")
    print("\n🌐 API Documentation: http://localhost:8000/docs")

def main():
    """Main setup function"""
    print("🚀 Autogen Backend Quick Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment file
    if not setup_environment_file():
        print("❌ Failed to setup environment file")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
