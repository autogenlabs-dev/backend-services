# How to Get a Fresh JWT Token for Testing

Your JWT token has **expired**. Here's how to get a fresh one:

## Method 1: From Browser Console (Easiest)

1. Open your React app in the browser (http://localhost:3000)
2. Make sure you're logged in
3. Open the browser console (F12)
4. Run this command:
   ```javascript
   await window.Clerk.session.getToken();
   ```
5. Copy the token that's printed
6. Replace the `JWT_TOKEN` variable in `test_component_api_with_token.py`

## Method 2: From Network Tab

1. Open your React app in the browser
2. Open DevTools → Network tab
3. Make any API request (like viewing components)
4. Look for the request in the Network tab
5. Click on it and go to "Headers"
6. Find the "Authorization" header
7. Copy the token (everything after "Bearer ")

## Method 3: Intercept in Code

Add this to your React app temporarily:

```javascript
// In your React app
useEffect(() => {
  const getToken = async () => {
    const token = await window.Clerk.session.getToken();
    console.log("🔑 Fresh JWT Token:", token);
  };
  getToken();
}, []);
```

## Then Run the Test Again

Once you have a fresh token:

```bash
# Edit the token in the file
nano test_component_api_with_token.py

# Run the test
python3 test_component_api_with_token.py
```

## Token Expiration Info

Your current token expired at: **2025-01-25 18:04:14 UTC**

JWT tokens typically expire after:

- 1 hour (default for Clerk)
- Check your Clerk dashboard for exact settings

## Alternative: Test Without JWT (Using Email/Password)

If you want to test without dealing with JWT expiration, you can use the comprehensive test script which creates its own session:

```bash
python3 comprehensive_api_test_all.py
```

This script will:

1. Register a new test user
2. Login and get a fresh token automatically
3. Test all endpoints
4. Generate a detailed report
