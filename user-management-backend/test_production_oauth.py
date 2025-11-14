#!/usr/bin/env python3
"""Test script to check Google OAuth endpoint on production server."""

import asyncio
import httpx
import sys
import ssl
from urllib.parse import urlparse

async def test_oauth_endpoints():
    """Test OAuth endpoints on production server."""
    
    production_base_url = "https://api.codemurf.com"
    
    # Test endpoints
    test_endpoints = [
        "/api/auth/providers",
        "/api/auth/google/login",
        "/api/auth/google/callback",
        "/api/auth/debug/oauth",
        "/health",
        "/"
    ]
    
    print(f"🔍 Testing OAuth endpoints on {production_base_url}")
    print("=" * 60)
    
    # Create SSL context that bypasses certificate verification for testing
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with httpx.AsyncClient(follow_redirects=False, verify=False) as client:
        for endpoint in test_endpoints:
            url = f"{production_base_url}{endpoint}"
            print(f"\n📍 Testing: {url}")
            
            try:
                response = await client.get(url, timeout=10.0)
                
                print(f"   Status Code: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if endpoint == "/api/auth/providers":
                            print(f"   Available providers: {list(data.get('providers', []))}")
                        elif endpoint == "/api/auth/debug/oauth":
                            print(f"   OAuth Debug Info:")
                            for provider, config in data.get('oauth_providers', {}).items():
                                print(f"     - {provider}: configured={config.get('configured')}")
                        else:
                            print(f"   Response: {str(data)[:200]}...")
                    except:
                        print(f"   Response: {response.text[:200]}...")
                elif response.status_code == 302:
                    location = response.headers.get('location', 'No location header')
                    print(f"   Redirect to: {location}")
                elif response.status_code == 404:
                    print(f"   ❌ 404 Not Found - Endpoint may not exist")
                else:
                    print(f"   Response: {response.text[:200]}...")
                    
            except httpx.TimeoutException:
                print(f"   ❌ Timeout - Request took too long")
            except httpx.ConnectError:
                print(f"   ❌ Connection Error - Could not connect to server")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🔍 Testing OAuth login flow simulation...")
    
    # Test the OAuth login endpoint specifically
    login_url = f"{production_base_url}/api/auth/google/login"
    print(f"\n📍 Testing OAuth Login: {login_url}")
    
    try:
        async with httpx.AsyncClient(follow_redirects=False, verify=False) as client:
            response = await client.get(login_url, timeout=10.0)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('location', 'No location header')
                print(f"   ✅ Redirect to Google OAuth: {location[:100]}...")
                
                # Check if it's redirecting to Google
                if "accounts.google.com" in location:
                    print("   ✅ Correctly redirecting to Google OAuth")
                else:
                    print(f"   ❌ Not redirecting to Google: {location}")
            elif response.status_code == 404:
                print("   ❌ 404 Not Found - OAuth login endpoint not available")
            else:
                print(f"   Unexpected response: {response.text[:200]}...")
                
    except Exception as e:
        print(f"   ❌ Error testing OAuth login: {str(e)}")

async def test_server_info():
    """Test basic server information."""
    
    production_base_url = "https://api.codemurf.com"
    
    print(f"\n🔍 Checking server information...")
    print("=" * 60)
    
    async with httpx.AsyncClient(verify=False) as client:
        # Test root endpoint
        try:
            response = await client.get(f"{production_base_url}/", timeout=10.0)
            print(f"Root endpoint ({production_base_url}/): {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error accessing root endpoint: {e}")
        
        # Test health endpoint
        try:
            response = await client.get(f"{production_base_url}/health", timeout=10.0)
            print(f"Health endpoint ({production_base_url}/health): {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error accessing health endpoint: {e}")
        
        # Test docs endpoint
        try:
            response = await client.get(f"{production_base_url}/docs", timeout=10.0)
            print(f"Docs endpoint ({production_base_url}/docs): {response.status_code}")
        except Exception as e:
            print(f"Error accessing docs endpoint: {e}")

if __name__ == "__main__":
    print("🚀 Starting Production OAuth Test")
    print("=" * 60)
    
    asyncio.run(test_server_info())
    asyncio.run(test_oauth_endpoints())
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")