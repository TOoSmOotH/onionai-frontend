"""
Configuration management for the frontend application.
"""
from typing import Optional
from pydantic import BaseSettings, Field
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings with environment variable loading and validation.
    
    All settings can be overridden with environment variables.
    """
    # AWS Configuration
    AWS_REGION: str = Field(..., description="AWS Region")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(None, description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(None, description="AWS Secret Access Key")

    # Cognito Configuration
    COGNITO_USER_POOL_ID: str = Field(..., description="Cognito User Pool ID")
    COGNITO_CLIENT_ID: str = Field(..., description="Cognito Client ID")
    COGNITO_CLIENT_SECRET: Optional[str] = Field(None, description="Cognito Client Secret")

    # API Configuration
    API_URL: str = Field(..., description="Backend API URL")
    API_VERSION: str = Field("v1", description="API Version")
    API_TIMEOUT: int = Field(30, description="API Timeout in seconds")

    # Rate Limiting
    ANONYMOUS_RATE_LIMIT: int = Field(10, description="Rate limit for anonymous users")
    AUTHENTICATED_RATE_LIMIT: int = Field(50, description="Rate limit for authenticated users")
    RATE_LIMIT_WINDOW_HOURS: int = Field(1, description="Rate limit window in hours")

    # Application Configuration
    DEBUG: bool = Field(False, description="Debug mode")
    ENVIRONMENT: str = Field("production", description="Environment (development/staging/production)")
    CLIENT_VERSION: str = Field("1.0.0", description="Client version")
    ENABLE_ANALYTICS: bool = Field(True, description="Enable analytics tracking")
    ENABLE_ERROR_REPORTING: bool = Field(True, description="Enable error reporting")

    # Streamlit Configuration
    STREAMLIT_SERVER_PORT: int = Field(8501, description="Streamlit server port")
    STREAMLIT_SERVER_ADDRESS: str = Field("0.0.0.0", description="Streamlit server address")
    STREAMLIT_THEME_BASE: str = Field("light", description="Default theme (light/dark)")
    
    class Config:
        """Pydantic configuration class."""
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()

def get_environment() -> str:
    """
    Get the current environment name.
    
    Returns:
        str: Current environment (development/staging/production)
    """
    return get_settings().ENVIRONMENT

def is_development() -> bool:
    """
    Check if running in development environment.
    
    Returns:
        bool: True if in development environment
    """
    return get_environment() == "development"

def is_debug_enabled() -> bool:
    """
    Check if debug mode is enabled.
    
    Returns:
        bool: True if debug mode is enabled
    """
    return get_settings().DEBUG