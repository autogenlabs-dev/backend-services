from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "mongodb://localhost:27017/user_management_db" # Changed to MongoDB
    redis_url: str = "redis://localhost:6379"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""  # Empty for local development
    
    # JWT
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Stripe
    stripe_secret_key: str = "sk_test_51RVi9b00tZAh2watNguPPSVIAwj7mll7RsiqeXfWIvR6JbwsO1vW2j4KWFlh8Tgkpozue2zq993aKn59wCRLZK5O00sbBOVXzr"
    stripe_publishable_key: str = "pk_test_51RVi9b00tZAh2watbNFlPjw4jKS02yZbKHQ1t97GcyMTOGLwcL8QhzxDSGtGu2EAJP4DHcEWOkut5N0CCTnuqBgh00p44dvGCb"
    stripe_webhook_secret: str = "whsec_your_webhook_secret"
    
    # Application
    app_name: str = "User Management Backend"
    debug: bool = True
    api_v1_str: str = "/api"
    
    # CORS
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # OAuth
    oauth_providers: List[str] = ["openrouter", "glama", "requesty", "aiml"]
    # OAuth Client Credentials (add your actual credentials to .env file)
    openrouter_client_id: str = "your_openrouter_client_id"
    openrouter_client_secret: str = "your_openrouter_client_secret"
    glama_client_id: str = "your_glama_client_id"
    glama_client_secret: str = "your_glama_client_secret"
    requesty_client_id: str = "your_requesty_client_id"
    requesty_client_secret: str = "your_requesty_client_secret"
    aiml_client_id: str = "your_aiml_client_id"
    aiml_client_secret: str = "your_aiml_client_secret"
    
    # LLM Provider API Keys
    openrouter_api_key: str = "your_openrouter_api_key"
    glama_api_key: str = "your_glama_api_key"
    requesty_api_key: str = "your_requesty_api_key"
    aiml_api_key: str = "your_aiml_api_key"
    
    # A4F API Key for VS Code Extension
    a4f_api_key: str = "ddc-a4f-a480842d898b49d4a15e14800c2f3c72"
    a4f_base_url: str = "https://api.a4f.co/v1"
    
    # Rate Limiting
    default_rate_limit_per_minute: int = 60
    pro_rate_limit_per_minute: int = 300
    enterprise_rate_limit_per_minute: int = 1000
    
    class Config:
        env_file = ".env"


settings = Settings()
