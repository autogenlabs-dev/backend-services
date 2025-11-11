# CodeMurf OAuth Quick Reference

## 🔐 Your Google OAuth Configuration

### Client Details
- **Client Name:** codemurf
- **Client ID:** `37099745939-4v685b95lv9r2306l1edq4s7dpnk05vd.apps.googleusercontent.com`
- **Client Secret:** `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`

### Redirect URIs
✅ **VS Code Extension (PKCE):** `vscode://codemurf.codemurf-extension/auth-callback`  
✅ **VS Code Extension (Legacy):** `vscode://codemurf.codemurf-extension/kilocode`  
✅ **Production API:** `https://api.codemurf.com/api/auth/google/callback`  
✅ **Development API:** `http://localhost:8000/api/auth/google/callback`

---

## 🌐 Authorized URLs

### JavaScript Origins
✅ **Production:** `https://codemurf.com`  
✅ **Development:** `http://localhost:3000`

### Redirect URIs
✅ **Production:** `https://api.codemurf.com/api/auth/google/callback`  
✅ **Development:** `http://localhost:8000/api/auth/google/callback`

---

## 🚀 Testing Commands

### Development Environment

**Test OAuth Login:**
```bash
curl -I "http://localhost:8000/api/auth/google/login?state=test&code_challenge=test&code_challenge_method=S256"
```
Expected: `302 Found` → Redirects to Google

**Test Token Exchange:**
```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "authorization_code",
    "code": "test",
    "code_verifier": "test",
    "redirect_uri": "vscode://codemurf.codemurf-extension/auth-callback"
  }'
```
Expected: `{"detail":"Invalid or expired authorization code"}`

---

## 📦 Docker Setup

### Start Services
```bash
cd /home/cis/Downloads/backend-services/user-management-backend
docker compose up -d --build
```

### Check Status
```bash
docker ps
docker logs user-management-backend-api-1
curl http://localhost:8000/health
```

### Restart After Code Changes
```bash
docker compose down
docker compose up -d --build
```

---

## 🧪 Run Tests
```bash
python3 test_pkce_flow.py
```

---

## 📚 Documentation
- **API Docs:** http://localhost:8000/docs
- **Implementation:** `PKCE_IMPLEMENTATION_COMPLETE.md`
- **Configuration:** `OAUTH_CONFIGURATION_GUIDE.md`
- **Test Results:** `PKCE_TEST_RESULTS.md`
- **Auth Spec:** `authdoc.md`

---

## ⚡ Quick Status Check
```bash
# Backend health
curl http://localhost:8000/health

# Available endpoints
curl http://localhost:8000/openapi.json | grep -o '"\/api\/auth\/[^"]*"'

# Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

**Status:** ✅ All systems operational  
**Environment:** Development (Docker)  
**Last Verified:** November 11, 2025
