"""Configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
from functools import lru_cache
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = ""  # Must be set via environment variable for SaaS
    
    # Security
    SECRET_KEY: str = ""  # Must be set via environment variable for SaaS
    JWT_SECRET_KEY: str = ""  # Must be set via environment variable for SaaS
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # OLLAMA
    OLLAMA_URL: str = "http://localhost:11434"
    
    # Backend URL (for internal API calls)
    BACKEND_URL: Optional[str] = None  # If None, will be constructed from HOST:PORT
    
    # CORS - Allow all origins in development
    CORS_ORIGINS: List[str] = ["*"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS_ORIGINS from JSON string or list."""
        if isinstance(v, str):
            # Remove any extra quotes or brackets
            v = v.strip()
            # Try to parse as JSON first
            try:
                # Handle JSON array string like '["http://localhost:3000", ...]'
                if v.startswith('[') and v.endswith(']'):
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return parsed
                # Handle single JSON string
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, str):
                    # Single string, return as list
                    return [parsed]
            except (json.JSONDecodeError, ValueError):
                # If not JSON, treat as comma-separated string
                if ',' in v:
                    # Remove brackets if present
                    v = v.strip('[]')
                    return [origin.strip().strip('"').strip("'") for origin in v.split(',')]
                else:
                    return [v.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    GRAFANA_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "backend.log"
    LOG_DIR: str = "logs"
    
    # AWS
    AWS_REGION: Optional[str] = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Payment Gateway
    PAYMENT_GATEWAY_API_KEY: Optional[str] = None
    PAYMENT_GATEWAY_SECRET: Optional[str] = None
    
    # Application Paths
    MEMORY_DIR: str = "memory"
    SETTINGS_FILE: str = "memory/settings.json"
    CHAT_LOG_FILE: str = "logs/chat.log"
    
    # Security AI - 100% Local/Offline Mode
    OFFLINE_MODE: bool = True  # Block all external connections
    SECURITY_AI_ENABLED: bool = True
    SECURITY_AI_LOG_PATHS: List[str] = [
        "/var/log/nginx/access.log",
        "/var/log/nginx/error.log",
        "/var/log/auth.log",
        "/var/log/app/backend.log",
    ]
    SECURITY_AI_AUTO_RESPONSE: bool = False  # Enable auto-response actions
    SECURITY_AI_USE_OLLAMA: bool = True  # Use local Ollama for AI explanations
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

