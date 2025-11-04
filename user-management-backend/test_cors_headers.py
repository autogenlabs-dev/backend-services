#!/usr/bin/env python3
"""Test script to verify CORS headers and detect duplicates"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def test_cors_headers():
    """Test CORS headers for production URLs"""
    
    print("=== CORS Headers Test ===")
    print(f"Environment: {getattr(settings, 'environment', 'development')}")
    print(f"CORS Origins: {settings.backend_cors_origins}")
    print()
    
    # Test URLs
    test_urls = [
        ("https://api.codemurf.com/health", "https://codemurf.com"),
        ("https://api.codemurf.com/health", "https://www.codemurf.com"),
        ("https://api.codemurf.com/api/auth/me", "https://codemurf.com"),
    ]
    
    for url, origin in test_urls:
        print(f"Testing: {url}")
        print(f"Origin: {origin}")
        
        try:
            # Test preflight request
            response = requests.options(
                url,
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization"
                },
                timeout=10,
                verify=False  # Ignore SSL for testing
            )
            
            print(f"Status: {response.status_code}")
            
            # Check CORS headers
            cors_headers = {}
            for header, value in response.headers.items():
                if header.lower().startswith('access-control-'):
                    cors_headers[header] = value
                    print(f"  {header}: {value}")
                    
                    # Check for duplicate values
                    if ',' in value and header.lower() == 'access-control-allow-origin':
                        origins = [o.strip() for o in value.split(',')]
                        if len(set(origins)) != len(origins):
                            print(f"  ⚠️  DUPLICATE ORIGINS DETECTED: {origins}")
                        elif len(origins) > 1:
                            print(f"  ⚠️  MULTIPLE ORIGINS IN SINGLE HEADER: {origins}")
            
            if not cors_headers:
                print("  ❌ No CORS headers found")
            else:
                print("  ✅ CORS headers present")
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")
        
        print()
    
    # Test local development
    print("=== Local Development Test ===")
    try:
        response = requests.get(
            "http://localhost:8000/health",
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )
        
        print(f"Local Status: {response.status_code}")
        
        cors_headers = {}
        for header, value in response.headers.items():
            if header.lower().startswith('access-control-'):
                cors_headers[header] = value
                print(f"  {header}: {value}")
                
                # Check for duplicates in local
                if ',' in value and header.lower() == 'access-control-allow-origin':
                    origins = [o.strip() for o in value.split(',')]
                    if len(set(origins)) != len(origins):
                        print(f"  ⚠️  DUPLICATE ORIGINS DETECTED LOCALLY: {origins}")
        
        if not cors_headers:
            print("  ❌ No CORS headers found locally")
        else:
            print("  ✅ Local CORS headers present")
            
    except requests.exceptions.RequestException as e:
        print(f"Local server not running or failed: {e}")

if __name__ == "__main__":
    test_cors_headers()
