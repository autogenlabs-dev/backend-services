#!/usr/bin/env python3
"""
Quick login test with known credentials
"""
import requests
import json

def test_login():
    """Test login with known credentials"""
    
    # Known working credentials
    credentials = {
        "email": "testuser_20250720_234038@example.com",
        "password": "TestPassword123!"
    }
    
    print("🔐 Testing Login with Known Credentials")
    print("=" * 50)
    print(f"📧 Email: {credentials['email']}")
    print(f"🔑 Password: {credentials['password']}")
    
    try:
        # Login
        response = requests.post(
            "http://localhost:8000/auth/login-json",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token', '')
            
            print("✅ Login Successful!")
            print(f"🔑 Access Token: {access_token[:50]}...")
            print(f"🔄 Refresh Token: {data.get('refresh_token', 'N/A')[:50]}...")
            
            # Test authenticated request
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(
                "http://localhost:8000/auth/me",
                headers=auth_headers
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                print("✅ Authenticated Request Successful!")
                print(f"👤 User: {user_data}")
            else:
                print(f"❌ Auth request failed: {user_response.status_code}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
