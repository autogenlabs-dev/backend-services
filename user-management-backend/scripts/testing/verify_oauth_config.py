
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_oauth_endpoint(provider):
    print(f"\nTesting {provider} Auth...")
    url = f"{BASE_URL}/api/auth/{provider}/login"
    try:
        # Don't follow redirects so we can check the Location header
        response = requests.get(url, allow_redirects=False)
        
        if response.status_code in [302, 307]:
            location = response.headers.get("Location", "")
            if provider == "google" and "accounts.google.com" in location:
                print(f"✅ PASS - {provider} redirects to Google")
                print(f"   URL: {location[:60]}...")
            elif provider == "github" and "github.com/login/oauth" in location:
                print(f"✅ PASS - {provider} redirects to GitHub")
                print(f"   URL: {location[:60]}...")
            else:
                print(f"❌ FAIL - {provider} unexpected redirect")
                print(f"   Location: {location}")
                return False
        else:
            print(f"❌ FAIL - {provider} returned code {response.status_code}")
            print(f"   Body: {response.text}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ FAIL - {provider} exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("Checking OAuth Configurations...")
    google_ok = test_oauth_endpoint("google")
    github_ok = test_oauth_endpoint("github")
    
    if google_ok and github_ok:
        print("\n✨ All OAuth endpoints reachable!")
    else:
        print("\n⚠️ Some OAuth checks failed. Check client IDs/secrets.")
        sys.exit(1)
