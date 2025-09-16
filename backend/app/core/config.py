from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration values."""

    app_name: str = Field(default="PlantMates API")
    debug: bool = Field(default=False)
    database_url: str = Field(default="sqlite:///./plantmates.db")
    default_radius_miles: int = Field(default=10, ge=1)
    max_radius_miles: int = Field(default=50, ge=1)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()
