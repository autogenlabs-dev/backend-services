# Future Auth (Backend)

Unused/legacy auth code saved for future reference.

## Files

| File            | Purpose                           |
| --------------- | --------------------------------- |
| `clerk_auth.py` | Clerk authentication (deprecated) |
| `jwt_backup.py` | Old JWT implementation backup     |
| `jwt_fixed.py`  | Another JWT variant               |
| `legacy.py`     | Legacy API endpoints              |

## Active Auth Files

These files are still in use:

| File                         | Purpose                                               |
| ---------------------------- | ----------------------------------------------------- |
| `api/auth.py`                | Main auth endpoints (Google, GitHub, register, login) |
| `auth/unified_auth.py`       | JWT + API key validation, auto-creates users          |
| `auth/oauth.py`              | OAuth provider configs                                |
| `auth/jwt.py`                | JWT creation/validation                               |
| `auth/api_key_auth_clean.py` | API key service                                       |
| `auth/dependencies.py`       | Auth dependencies                                     |
