import os
from typing import Any, Dict, Optional
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EventSphere"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super_secret_signing_key_for_jwt_auth_123456"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database Configurations
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "eventsphere"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str) and v:
            return v
        
        # Read fields from data if present, otherwise environment variables
        data = info.data
        user = data.get("POSTGRES_USER") or os.getenv("POSTGRES_USER", "postgres")
        password = data.get("POSTGRES_PASSWORD") or os.getenv("POSTGRES_PASSWORD", "postgres")
        server = data.get("POSTGRES_SERVER") or os.getenv("POSTGRES_SERVER", "localhost")
        port = data.get("POSTGRES_PORT") or os.getenv("POSTGRES_PORT", "5432")
        db = data.get("POSTGRES_DB") or os.getenv("POSTGRES_DB", "eventsphere")

        return f"postgresql://{user}:{password}@{server}:{port}/{db}"

    # Email Service Configurations
    EMAIL_BACKEND: str = "console"  # console, smtp, resend
    EMAIL_FROM: str = "noreply@eventsphere.com"

    # SMTP config
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Resend config
    RESEND_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
