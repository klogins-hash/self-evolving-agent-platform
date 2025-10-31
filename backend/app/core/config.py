from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # API Configuration
    api_title: str = "Self-Evolving Agent Platform"
    api_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./agents.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI/ML APIs
    groq_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Agent Configuration
    max_agents: int = 10
    default_agent_timeout: int = 300  # seconds
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
