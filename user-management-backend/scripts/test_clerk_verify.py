"""Small CLI helper to verify a Clerk token using the JWKS verifier.

Usage:
  - Set `PYTHONPATH` to the project root or run with project's python
  - Provide token via `CLERK_TOKEN` env or as first arg

Example:
  CLERK_TOKEN=<token> PYTHONPATH=. /path/to/python scripts/test_clerk_verify.py
"""
import os
import sys
from typing import Optional

def main():
    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = os.getenv("CLERK_TOKEN")

    if not token:
        print("Provide a Clerk token as argument or in CLERK_TOKEN env")
        sys.exit(2)

    # Import verifier
    try:
        from app.auth.clerk_verifier import verify_clerk_token
    except Exception as e:
        print("Failed to import verifier:", e)
        sys.exit(1)

    try:
        claims = verify_clerk_token(token)
        print("Token verified. Claims:")
        for k, v in claims.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print("Verification failed:", e)
        sys.exit(3)

if __name__ == '__main__':
    main()
