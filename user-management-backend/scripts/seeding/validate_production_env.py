#!/usr/bin/env python3
"""
Production Environment Validation Script
Run this to check if your production environment is properly configured.
"""

import os
import re
from typing import List, Tuple

def load_env_file(filename: str) -> dict:
    """Load environment variables from file."""
    env_vars = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print(f"❌ {filename} not found!")
        return {}
    return env_vars

def validate_production_env() -> List[Tuple[str, str, bool]]:
    """Validate production environment configuration."""
    env_vars = load_env_file('.env.production')
    if not env_vars:
        return []
    
    validations = []
    
    # JWT Secret Key
    jwt_key = env_vars.get('JWT_SECRET_KEY', '')
    jwt_valid = len(jwt_key) >= 32 and not jwt_key.startswith('CHANGE-THIS')
    validations.append(('JWT_SECRET_KEY', 'Strong secret key (32+ chars)', jwt_valid))
    
    # Stripe Keys
    stripe_secret = env_vars.get('STRIPE_SECRET_KEY', '')
    stripe_secret_valid = stripe_secret.startswith('sk_live_') and len(stripe_secret) > 20
    validations.append(('STRIPE_SECRET_KEY', 'Live Stripe secret key', stripe_secret_valid))
    
    stripe_pub = env_vars.get('STRIPE_PUBLISHABLE_KEY', '')
    stripe_pub_valid = stripe_pub.startswith('pk_live_') and len(stripe_pub) > 20
    validations.append(('STRIPE_PUBLISHABLE_KEY', 'Live Stripe publishable key', stripe_pub_valid))
    
    # Razorpay Keys
    razorpay_id = env_vars.get('RAZORPAY_KEY_ID', '')
    razorpay_id_valid = razorpay_id.startswith('rzp_live_') and len(razorpay_id) > 15
    validations.append(('RAZORPAY_KEY_ID', 'Live Razorpay key ID', razorpay_id_valid))
    
    razorpay_secret = env_vars.get('RAZORPAY_KEY_SECRET', '')
    razorpay_secret_valid = len(razorpay_secret) > 20 and not razorpay_secret.startswith('REPLACE_WITH')
    validations.append(('RAZORPAY_KEY_SECRET', 'Live Razorpay secret', razorpay_secret_valid))
    
    # CORS Origins
    cors_origins = env_vars.get('BACKEND_CORS_ORIGINS', '')
    cors_valid = 'yourdomain.com' not in cors_origins and 'https://' in cors_origins
    validations.append(('BACKEND_CORS_ORIGINS', 'Production domains', cors_valid))
    
    # Database
    db_url = env_vars.get('DATABASE_URL', '')
    db_valid = 'mongodb' in db_url and len(db_url) > 20
    validations.append(('DATABASE_URL', 'MongoDB connection', db_valid))
    
    # Environment
    environment = env_vars.get('ENVIRONMENT', '')
    env_valid = environment == 'production'
    validations.append(('ENVIRONMENT', 'Set to production', env_valid))
    
    # Debug mode
    debug = env_vars.get('DEBUG', 'True')
    debug_valid = debug.lower() == 'false'
    validations.append(('DEBUG', 'Disabled for production', debug_valid))
    
    return validations

def main():
    print("🔍 Validating Production Environment Configuration...\n")
    
    validations = validate_production_env()
    if not validations:
        print("❌ Could not load .env.production file!")
        return
    
    passed = 0
    failed = 0
    
    for key, description, is_valid in validations:
        status = "✅" if is_valid else "❌"
        print(f"{status} {key}: {description}")
        if is_valid:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n🔧 To fix the failed items:")
        print("1. Update your .env.production file with the correct values")
        print("2. Get live API keys from your service providers")
        print("3. Replace placeholder values with actual credentials")
        print("4. Set DEBUG=False for production")
        print("5. Update CORS origins with your actual domains")
    else:
        print("\n🎉 All production environment checks passed!")

if __name__ == "__main__":
    main()
