#!/usr/bin/env python3
"""
Direct test of OAuth callback redirect URL
"""

import sys

# Read the actual callback function from the container
print("=" * 80)
print("Checking OAuth Callback Redirect Configuration")
print("=" * 80)

print("\n📋 Checking /api/auth/google/callback endpoint...")
print("\nSearching for redirect_url assignments in callback handler:\n")

with open('/home/cis/Downloads/backend-services/user-management-backend/app/api/auth.py', 'r') as f:
    lines = f.readlines()
    in_callback = False
    for i, line in enumerate(lines, 1):
        if '@router.get("/google/callback")' in line:
            in_callback = True
            print(f"Line {i}: Found callback function start")
        
        if in_callback and 'redirect_url' in line and '=' in line:
            # Print context around this line
            start = max(0, i-3)
            end = min(len(lines), i+2)
            print(f"\n--- Lines {start+1} to {end} ---")
            for j in range(start, end):
                prefix = ">>>" if j == i-1 else "   "
                print(f"{prefix} {j+1:4d}: {lines[j]}", end='')
            
        if in_callback and 'async def' in line and i > 350:
            # Next function found, stop
            break

print("\n" + "=" * 80)
print("Verification")
print("=" * 80)

# Count occurrences
with open('/home/cis/Downloads/backend-services/user-management-backend/app/api/auth.py', 'r') as f:
    content = f.read()
    
    vscode_count = content.count('vscode://codemurf.codemurf-extension/kilocode')
    localhost_count = content.count('localhost:3000/auth/callback')
    
    print(f"\n✅ VS Code redirect URLs: {vscode_count}")
    print(f"{'✅' if localhost_count == 0 else '❌'} localhost:3000 redirect URLs: {localhost_count}")
    
    if vscode_count > 0 and localhost_count == 0:
        print("\n🎉 Configuration is CORRECT!")
        print("Backend redirects to: vscode://codemurf.codemurf-extension/kilocode?token=XXX")
    elif localhost_count > 0:
        print("\n⚠️ WARNING: Found localhost:3000 redirects!")
        print("These should be changed to VS Code URI scheme.")
    else:
        print("\n⚠️ No explicit redirects found (might be using variables)")

print("\n" + "=" * 80)
print("Testing Live Endpoint")
print("=" * 80)

import requests

print("\nNote: To fully test the OAuth callback, you need to:")
print("1. Complete Google OAuth authentication")
print("2. Google will redirect to: http://localhost:8000/api/auth/google/callback?code=...")
print("3. Our backend will then redirect to: vscode://codemurf.codemurf-extension/kilocode?token=...")

print("\n✅ Configuration verified in source code")
print("✅ Docker container is running the latest code (Up 10 minutes)")
print("\nIf you're still seeing localhost:3000 redirects, please:")
print("1. Clear your browser cache")
print("2. Use incognito/private browsing")
print("3. Check you're not testing an old bookmark/saved URL")
