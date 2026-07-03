from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./heatseeker.db"
    
    # API Keys
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    youtube_api_key: Optional[str] = None
    lastfm_api_key: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # App Settings
    debug: bool = True
    secret_key: str = "dev-secret-key"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate Limits
    spotify_rate_limit: int = 100
    youtube_rate_limit: int = 1000
    api_request_delay: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()