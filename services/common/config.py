"""Base settings for every service. Values come from environment variables or `.env`.

Each service extends `Settings` with its own fields (see `calculator/config.py`).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
