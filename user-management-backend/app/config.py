from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import os
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.production" if os.getenv("ENVIRONMENT") == "production" else ".env",
        extra="ignore"  # This will ignore extra environment variables
    )
    
    # Database - MUST be set via environment variables in production
    database_url: str = "mongodb://mongodb:27017/user_management_db"  # Docker default
    redis_url: str = "redis://redis:6379"  # Docker default
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    
    # JWT - jwt_secret_key MUST be set via environment variable in production
    jwt_secret_key: str = ""  # REQUIRED: Set JWT_SECRET_KEY env var
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # Increased for better UX
    refresh_token_expire_days: int = 7
    
    # Stripe - Set via environment variables
    stripe_secret_key: str = ""  # Set STRIPE_SECRET_KEY env var
    stripe_publishable_key: str = ""  # Set STRIPE_PUBLISHABLE_KEY env var
    stripe_webhook_secret: str = ""  # Set STRIPE_WEBHOOK_SECRET env var
    
    # Razorpay - Set via environment variables
    razorpay_key_id: str = ""  # Set RAZORPAY_KEY_ID env var
    razorpay_key_secret: str = ""  # Set RAZORPAY_KEY_SECRET env var
    
    # Application
    app_name: str = "User Management Backend"
    debug: bool = False  # IMPORTANT: Default to False for production safety
    api_v1_str: str = "/api"
    project_name: str = "User Management API"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Production URLs
    production_frontend_url: str = "https://codemurf.com"
    production_backend_url: str = "https://api.codemurf.com"
    
    # CORS
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080", "https://codemurf.com", "https://www.codemurf.com"]
    
    @field_validator('backend_cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v.split(',')
        return v
    
    # OAuth
    oauth_providers: List[str] = ["openrouter", "google", "github"]

    # OAuth Client Credentials - Set via environment variables
    openrouter_client_id: str = ""  # Set OPENROUTER_CLIENT_ID env var
    openrouter_client_secret: str = ""  # Set OPENROUTER_CLIENT_SECRET env var
    google_client_id: str = ""  # Set GOOGLE_CLIENT_ID env var
    google_client_secret: str = ""  # Set GOOGLE_CLIENT_SECRET env var
    google_redirect_uri: str = "https://api.codemurf.com/api/auth/google/callback"
    github_client_id: str = ""  # Set GITHUB_CLIENT_ID env var
    github_client_secret: str = ""  # Set GITHUB_CLIENT_SECRET env var
    github_redirect_uri: str = "https://api.codemurf.com/api/auth/github/callback"
    
    # LLM Provider API Keys - Set via environment variables
    openrouter_api_key: str = ""  # Set OPENROUTER_API_KEY env var
    openrouter_provisioning_api_key: str = ""  # Provisioning key for per-user API keys
    openrouter_api_base: str = "https://openrouter.ai/api/v1"
    glama_api_key: str = ""  # Set GLAMA_API_KEY env var
    requesty_api_key: str = ""  # Set REQUESTY_API_KEY env var
    aiml_api_key: str = ""  # Set AIML_API_KEY env var
    
    # A4F API Key for VS Code Extension - Set via environment variable
    a4f_api_key: str = ""  # Set A4F_API_KEY env var
    a4f_base_url: str = "https://api.a4f.co/v1"
    
    # Rate Limiting
    default_rate_limit_per_minute: int = 60
    pro_rate_limit_per_minute: int = 300
    enterprise_rate_limit_per_minute: int = 1000


settings = Settings()
