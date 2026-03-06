from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings and environment variable configuration.
    """
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    GEMINI_API_KEY: str
    
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    
    # Allow loading from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Global settings instance
settings = Settings()
