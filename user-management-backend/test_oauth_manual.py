#!/usr/bin/env python3
"""
Manual OAuth Testing Script
Provides URLs for manual browser testing of OAuth flows
"""

import webbrowser
import time

# Configuration
BASE_URL = "http://localhost:8000"

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{'=' * 80}")
    print(f"{text.center(80)}")
    print(f"{'=' * 80}\n")

def print_info(text: str):
    """Print info message"""
    print(f"ℹ️  {text}")

def print_success(text: str):
    """Print success message"""
    print(f"✅ {text}")

def main():
    """Main function to provide OAuth testing URLs"""
    print_header("🔐 Manual OAuth Testing")
    
    providers = [
        {
            "name": "Google",
            "url": f"{BASE_URL}/auth/google/login",
            "description": "Google OAuth2 authentication"
        },
        {
            "name": "GitHub", 
            "url": f"{BASE_URL}/auth/github/login",
            "description": "GitHub OAuth authentication"
        },
        {
            "name": "OpenRouter",
            "url": f"{BASE_URL}/auth/openrouter/login", 
            "description": "OpenRouter OAuth authentication"
        }
    ]
    
    print_info("Available OAuth Providers:")
    for i, provider in enumerate(providers, 1):
        print(f"\n{i}. {provider['name']}")
        print(f"   URL: {provider['url']}")
        print(f"   Description: {provider['description']}")
    
    print_info("\n📋 Testing Instructions:")
    print("1. Choose a provider from the list above")
    print("2. Copy the URL or let this script open it in browser")
    print("3. Complete authentication in your browser")
    print("4. You should be redirected back to the application")
    print("5. Check server logs for successful authentication")
    
    # Ask user which provider to test
    try:
        choice = input(f"\nEnter provider number (1-{len(providers)}) or 'all' to open all: ").strip()
        
        if choice.lower() == 'all':
            for provider in providers:
                print_info(f"Opening {provider['name']} OAuth URL...")
                webbrowser.open(provider['url'])
                time.sleep(1)  # Small delay between openings
        elif choice.isdigit() and 1 <= int(choice) <= len(providers):
            provider = providers[int(choice) - 1]
            print_info(f"Opening {provider['name']} OAuth URL...")
            webbrowser.open(provider['url'])
        else:
            print_info("Invalid choice. Here are the URLs for manual testing:")
            for provider in providers:
                print(f"\n{provider['name']}: {provider['url']}")
                
    except KeyboardInterrupt:
        print_info("\nTesting cancelled by user")
    except Exception as e:
        print_info(f"Error: {e}")
    
    print_info("\n🔍 Debugging Tips:")
    print("- Check server logs for OAuth callback requests")
    print("- Verify OAuth client IDs and secrets are configured")
    print("- Ensure redirect URIs match in OAuth provider settings")
    print("- Check for CORS issues if callbacks fail")
    
    print_success("\nOAuth testing setup complete!")

if __name__ == "__main__":
    main()