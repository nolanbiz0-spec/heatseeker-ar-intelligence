import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings"""
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    secret_key: str = "your-super-secret-key-change-this"
    
    # Database Configuration
    database_url: str = "postgresql+asyncpg://heatseeker:password@localhost:5432/heatseeker"
    redis_url: str = "redis://localhost:6379/0"
    
    # Spotify API
    spotify_client_id: str
    spotify_client_secret: str
    
    # YouTube API
    youtube_api_key: str
    
    # Last.fm API
    lastfm_api_key: str
    lastfm_secret: str
    
    # MusicBrainz API
    musicbrainz_email: str
    
    # Rate Limiting Configuration
    spotify_rate_limit: int = 100  # requests per minute
    youtube_rate_limit: int = 10000  # units per day
    lastfm_rate_limit: int = 5  # requests per second
    musicbrainz_rate_limit: float = 1.0  # requests per second
    
    # Analysis Configuration
    velocity_window_days: list[int] = [7, 30, 90]
    authenticity_threshold: float = 0.7
    momentum_threshold: float = 0.8
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic migrations"""
        return self.database_url.replace("+asyncpg", "")


settings = Settings()