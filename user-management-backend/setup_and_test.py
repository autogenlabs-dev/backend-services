#!/usr/bin/env python3
"""
Setup and Test Runner for MongoDB-based User Management Backend
This script handles the complete setup and testing process.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "motor", 
        "beanie",
        "bcrypt",
        "httpx",
        "uvicorn"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"   ✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install {package}")
                return False
    
    return True

def check_mongodb_connection():
    """Check if MongoDB is running and accessible."""
    print("\n🍃 Checking MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        from app.config import settings
        
        # Extract host and port from database_url
        # Format: mongodb://localhost:27017/user_management_db
        if "mongodb://" in settings.database_url:
            url_parts = settings.database_url.replace("mongodb://", "").split("/")
            host_port = url_parts[0]
            
            if ":" in host_port:
                host, port = host_port.split(":")
                port = int(port)
            else:
                host = host_port
                port = 27017
        else:
            host = "localhost"
            port = 27017
        
        # Test connection
        client = MongoClient(host, port, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection
        client.close()
        
        print(f"   ✅ MongoDB is running on {host}:{port}")
        return True
        
    except Exception as e:
        print(f"   ❌ MongoDB connection failed: {e}")
        print("\n📝 To fix this:")
        print("   1. Install MongoDB: https://docs.mongodb.com/manual/installation/")
        print("   2. Start MongoDB service:")
        print("      - Windows: net start MongoDB")
        print("      - macOS/Linux: sudo systemctl start mongod")
        print("   3. Or use MongoDB Atlas (cloud): https://www.mongodb.com/atlas")
        return False

def run_command(description, command, check=True):
    """Run a system command with status reporting."""
    print(f"\n{description}")
    print(f"💻 Running: {' '.join(command)}")
    
    try:
        if check:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            if result.stdout:
                print(f"📤 Output: {result.stdout.strip()}")
            return True
        else:
            subprocess.run(command)
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"📤 Error: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        return False

async def main():
    """Main setup and test function."""
    print("🚀 MongoDB Backend Setup & Test Runner")
    print("=" * 50)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed!")
        return False
    
    # Step 2: Check MongoDB
    if not check_mongodb_connection():
        print("❌ MongoDB connection failed!")
        return False
    
    # Step 3: Initialize database
    print("\n🔧 Initializing MongoDB database...")
    try:
        from init_mongodb import init_database, create_test_user
        
        # Initialize database
        success = await init_database()
        if not success:
            print("❌ Database initialization failed!")
            return False
        
        # Create test user
        test_user = await create_test_user()
        if not test_user:
            print("❌ Test user creation failed!")
            return False
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    # Step 4: Start server (in background)
    print("\n🌐 Starting FastAPI server...")
    server_process = None
    try:
        # Start server in background
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        # Wait a moment for server to start
        await asyncio.sleep(3)
        
        if server_process.poll() is None:
            print("✅ Server started successfully on http://localhost:8000")
        else:
            print("❌ Server failed to start")
            return False
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    # Step 5: Run authentication tests
    print("\n🧪 Running authentication flow tests...")
    try:
        from test_auth_flow import AuthFlowTester
        
        tester = AuthFlowTester()
        test_success = await tester.run_full_test_suite()
        
        if test_success:
            print("\n🎉 All tests passed! Your backend is ready for VS Code integration.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        test_success = False
    
    finally:
        # Clean up server process
        if server_process and server_process.poll() is None:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
    
    return test_success

if __name__ == "__main__":
    print("📋 MongoDB Backend Setup & Test Script")
    print("🎯 This script will:")
    print("   1. Check and install dependencies")
    print("   2. Verify MongoDB connection")
    print("   3. Initialize database and create test data")
    print("   4. Start the FastAPI server")
    print("   5. Run authentication flow tests")
    print()
    
    try:
        success = asyncio.run(main())
        
        if success:
            print("\n✅ Setup and testing completed successfully!")
            print("🚀 Your backend is ready for VS Code extension integration!")
            sys.exit(0)
        else:
            print("\n❌ Setup or testing failed!")
            print("📝 Please check the error messages above and try again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup crashed: {e}")
        sys.exit(1)
