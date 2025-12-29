#!/usr/bin/env python3
"""
Docker Production Database Reset

Specialized script for dockerized MongoDB environments.
Works with docker-compose MongoDB services.

Usage:
    # From host machine
    docker exec -it backend-container python3 reset_live_db_docker.py --confirm
    
    # From inside container  
    python3 reset_live_db_docker.py --confirm
"""

import asyncio
import os
import sys
from reset_live_db import main as reset_main, print_connection_info

def check_docker_environment():
    """Check if running inside Docker container"""
    
    # Check for Docker indicators
    docker_indicators = [
        os.path.exists('/.dockerenv'),
        os.path.exists('/proc/1/cgroup') and 'docker' in open('/proc/1/cgroup').read(),
        os.environ.get('DOCKER_CONTAINER') == 'true'
    ]
    
    is_docker = any(docker_indicators)
    
    print("🐳 DOCKER ENVIRONMENT CHECK:")
    print("=" * 60)
    print(f"Running in Docker: {'✅ Yes' if is_docker else '❌ No'}")
    
    if is_docker:
        print("🔍 Container details:")
        
        # Container hostname
        hostname = os.environ.get('HOSTNAME', 'unknown')
        print(f"   Hostname: {hostname}")
        
        # Check for common environment variables
        env_vars = ['DOCKER_CONTAINER', 'CONTAINER_NAME', 'SERVICE_NAME']
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                print(f"   {var}: {value}")
    
    print()
    return is_docker

def check_mongodb_connection():
    """Check MongoDB connection in Docker environment"""
    
    print("📡 MONGODB CONNECTION CHECK:")
    print("=" * 60)
    
    from app.config import Settings
    settings = Settings()
    
    db_url = settings.database_url
    print(f"Database URL: {db_url}")
    
    # Common Docker MongoDB patterns
    if "mongodb://mongo:" in db_url:
        print("🐳 Detected: Docker Compose MongoDB service")
    elif "mongodb://localhost:" in db_url:
        print("🔗 Detected: Local MongoDB connection")
    elif "mongodb+srv://" in db_url:
        print("☁️  Detected: MongoDB Atlas (Cloud)")
    else:
        print("❓ Unknown MongoDB connection type")
    
    print()

async def docker_safe_reset():
    """Docker-safe version of database reset"""
    
    print("🐳 DOCKER DATABASE RESET")
    print("=" * 80)
    print()
    
    # Check environment
    is_docker = check_docker_environment()
    check_mongodb_connection()
    
    if not is_docker:
        print("⚠️  Warning: Not running in Docker container")
        print("Consider using the regular reset_live_db.py script")
        print()
    
    # Run the main reset function
    await reset_main()

if __name__ == "__main__":
    try:
        asyncio.run(docker_safe_reset())
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)