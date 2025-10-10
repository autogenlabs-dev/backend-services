#!/usr/bin/env python3
"""
Check which MongoDB the live API server is actually connecting to
by inspecting the running container's environment
"""
import subprocess
import json

print("\n" + "="*80)
print("🐳 CHECKING LIVE DOCKER CONTAINER CONFIGURATION")
print("="*80)

# Get container details
try:
    print("\n1️⃣ Checking Docker Container Environment...")
    result = subprocess.run(
        ['docker', 'inspect', 'user-management-backend-api-1'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        container_info = json.loads(result.stdout)[0]
        
        # Get environment variables
        env_vars = container_info.get('Config', {}).get('Env', [])
        
        print("\n🌍 Container Environment Variables:")
        print("   " + "─"*76)
        
        db_url = None
        for env in env_vars:
            if 'DATABASE' in env or 'MONGO' in env or 'DB' in env:
                print(f"   {env}")
                if env.startswith('DATABASE_URL='):
                    db_url = env.split('=', 1)[1]
        
        if db_url:
            print(f"\n   ✅ Active DATABASE_URL: {db_url}")
        else:
            print(f"\n   ⚠️  No DATABASE_URL found in container environment")
        
        # Check mounts/volumes
        print("\n📦 Container Volumes/Mounts:")
        mounts = container_info.get('Mounts', [])
        for mount in mounts:
            source = mount.get('Source', 'N/A')
            destination = mount.get('Destination', 'N/A')
            print(f"   {source} -> {destination}")
        
        # Check network
        print("\n🌐 Container Network:")
        networks = container_info.get('NetworkSettings', {}).get('Networks', {})
        for net_name, net_info in networks.items():
            print(f"   Network: {net_name}")
            print(f"   IP Address: {net_info.get('IPAddress', 'N/A')}")
            
    else:
        print(f"❌ Failed to inspect container: {result.stderr}")
        
except FileNotFoundError:
    print("❌ Docker command not found. Are you running on the EC2 server?")
except Exception as e:
    print(f"❌ Error: {e}")

# Check which MongoDB containers are running
print(f"\n{'='*80}")
print("2️⃣ Checking Running MongoDB Containers...")
print("="*80)

try:
    result = subprocess.run(
        ['docker', 'ps', '--filter', 'name=mongo', '--format', '{{.Names}}\t{{.Status}}\t{{.Ports}}'],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print("\n✅ MongoDB containers found:")
        print("   " + "─"*76)
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                print(f"   📦 {parts[0]}")
                if len(parts) > 1:
                    print(f"      Status: {parts[1]}")
                if len(parts) > 2:
                    print(f"      Ports: {parts[2]}")
    else:
        print("\n⚠️  No MongoDB containers found")
        
except Exception as e:
    print(f"❌ Error checking MongoDB containers: {e}")

# Check .env file in mounted volume
print(f"\n{'='*80}")
print("3️⃣ Checking .env File Configuration...")
print("="*80)

try:
    # Try to read .env from likely locations
    env_paths = [
        '/home/ubuntu/backend-services/user-management-backend/.env',
        './.env',
        '../.env'
    ]
    
    for env_path in env_paths:
        try:
            with open(env_path, 'r') as f:
                print(f"\n✅ Found .env at: {env_path}")
                print("   " + "─"*76)
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if 'DATABASE' in line or 'MONGO' in line or 'DB_' in line:
                            print(f"   {line}")
                break
        except FileNotFoundError:
            continue
    else:
        print("\n⚠️  No .env file found in common locations")
        
except Exception as e:
    print(f"❌ Error reading .env: {e}")

print(f"\n{'='*80}")
print("📋 SUMMARY")
print("="*80)
print("""
Check if the API container is connecting to:
• mongodb://mongodb:27017 (Docker network) ✅ Expected
• mongodb://localhost:27017 (Host network) ⚠️  Wrong for container
• MongoDB Atlas (cloud) ⚠️  Different database

The 'Invalid salt' error suggests the API is connecting to a database
with BCRYPT password hashes instead of SHA-256 hashes.
""")
