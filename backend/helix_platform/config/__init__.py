import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base Configuration class containing common settings for the Helix backend."""

    # General App Settings
    APP_NAME: str = "helix-backend"
    APP_VERSION: str = "1.0.0"
    ENV: str = "dev"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Logging Settings
    LOG_LEVEL: str = "INFO"

    # Persistence
    DATABASE_URL: str = "sqlite:///helix.db"

    # Security
    JWT_SECRET_KEY: str = "insecure-dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Telemetry (OpenTelemetry)
    OTEL_SERVICE_NAME: str = "helix-backend"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DevConfig(BaseConfig):
    """Development configuration settings."""

    ENV: Literal["dev"] = "dev"
    LOG_LEVEL: str = "DEBUG"


class ProdConfig(BaseConfig):
    """Production configuration settings with stricter constraints."""

    ENV: Literal["prod"] = "prod"
    LOG_LEVEL: str = "INFO"

    # Force database URL and secret key to be set in environment for production
    DATABASE_URL: str
    JWT_SECRET_KEY: str


@lru_cache
def get_settings() -> BaseConfig:
    """Returns the configuration instance.

    Loads the config based on the HELIX_ENV environment variable.
    """
    env = os.getenv("HELIX_ENV", "dev").lower()
    if env == "prod":
        return ProdConfig()  # type: ignore[call-arg]
    if env == "test":
        # Return development config with DEBUG log level for tests
        return DevConfig(LOG_LEVEL="DEBUG")
    return DevConfig()
