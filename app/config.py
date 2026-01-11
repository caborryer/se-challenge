from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    app_name: str = Field(default="User Management API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    
    database_url: str = Field(
        default="sqlite:///./user_management.db",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    gcp_project_id: str = Field(default="", env="GCP_PROJECT_ID")
    gcp_region: str = Field(default="us-central1", env="GCP_REGION")
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "testing", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

