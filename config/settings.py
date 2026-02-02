"""Application configuration settings."""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://lap_user:lap_password@localhost:5432/lap_db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "lap_db"
    DATABASE_USER: str = "lap_user"
    DATABASE_PASSWORD: str = "lap_password"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    DEBUG: bool = True
    
    # PNCP API Configuration
    PNCP_BASE_URL: str = "https://pncp.gov.br/api/consulta/v1"
    PNCP_TIMEOUT: int = 30
    PNCP_MAX_RETRIES: int = 3
    PNCP_RETRY_DELAY: int = 5
    
    # Scheduler Configuration
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "America/Sao_Paulo"
    COLLECTION_TIMES: str = "06:00,12:00,18:00,00:00"
    
    # Email Notifications
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@lap.com"
    
    # Application Settings
    APP_NAME: str = "LAP - Licitações Aparecida Plus"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_collection_times() -> List[str]:
    """Get collection times from settings."""
    return [time.strip() for time in settings.COLLECTION_TIMES.split(",")]
