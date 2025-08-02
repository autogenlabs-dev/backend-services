from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="mongodb://localhost:27017/user_management_db", env="DATABASE_URL")
    mongodb_url: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    mongodb_db_name: str = Field(default="user_management_db", env="MONGODB_DB_NAME")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    
    # JWT
    jwt_secret_key: str = Field(default="your-super-secret-jwt-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Stripe
    stripe_secret_key: str = Field(default="sk_test_", env="STRIPE_SECRET_KEY")
    stripe_publishable_key: str = Field(default="pk_test_", env="STRIPE_PUBLISHABLE_KEY")
    stripe_webhook_secret: str = Field(default="whsec_", env="STRIPE_WEBHOOK_SECRET")
    
    # Razorpay
    razorpay_key_id: str = Field(default="rzp_test_", env="RAZORPAY_KEY_ID")
    razorpay_key_secret: str = Field(default="test_secret_", env="RAZORPAY_KEY_SECRET")
    
    # Application
    app_name: str = Field(default="User Management Backend", env="APP_NAME")
    debug: bool = Field(default=True, env="DEBUG")
    api_v1_str: str = Field(default="/api", env="API_V1_STR")
    project_name: str = Field(default="User Management API", env="PROJECT_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # CORS
    backend_cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8080"], env="BACKEND_CORS_ORIGINS")
    
    # OAuth
    oauth_providers: List[str] = Field(default=["openrouter", "glama", "requesty", "aiml"], env="OAUTH_PROVIDERS")
    
    # OAuth Client Credentials
    openrouter_client_id: str = Field(default="", env="OPENROUTER_CLIENT_ID")
    openrouter_client_secret: str = Field(default="", env="OPENROUTER_CLIENT_SECRET")
    glama_client_id: str = Field(default="", env="GLAMA_CLIENT_ID")
    glama_client_secret: str = Field(default="", env="GLAMA_CLIENT_SECRET")
    requesty_client_id: str = Field(default="", env="REQUESTY_CLIENT_ID")
    requesty_client_secret: str = Field(default="", env="REQUESTY_CLIENT_SECRET")
    aiml_client_id: str = Field(default="", env="AIML_CLIENT_ID")
    aiml_client_secret: str = Field(default="", env="AIML_CLIENT_SECRET")
    
    # LLM Provider API Keys
    openrouter_api_key: str = Field(default="", env="OPENROUTER_API_KEY")
    glama_api_key: str = Field(default="", env="GLAMA_API_KEY")
    requesty_api_key: str = Field(default="", env="REQUESTY_API_KEY")
    aiml_api_key: str = Field(default="", env="AIML_API_KEY")
    
    # A4F API Key for VS Code Extension
    a4f_api_key: str = Field(default="ddc-a4f-a480842d898b49d4a15e14800c2f3c72", env="A4F_API_KEY")
    a4f_base_url: str = Field(default="https://api.a4f.co/v1", env="A4F_BASE_URL")
    
    # Rate Limiting
    default_rate_limit_per_minute: int = Field(default=60, env="DEFAULT_RATE_LIMIT_PER_MINUTE")
    pro_rate_limit_per_minute: int = Field(default=300, env="PRO_RATE_LIMIT_PER_MINUTE")
    enterprise_rate_limit_per_minute: int = Field(default=1000, env="ENTERPRISE_RATE_LIMIT_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
