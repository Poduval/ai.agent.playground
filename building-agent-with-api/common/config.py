"""Settings shared by every agent. Values come from environment variables or `.env`.

Each agent extends `Settings` with its own fields (see `calculator/config.py`).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Security: shared secret for local development. CHANGE IT outside localhost. ---
    a2a_bearer_token: str = "dev-a2a-token"  # A2A agents expect `Authorization: Bearer ...`

    # --- LLM: pick a provider preset, then optionally override model / URL / key ---
    llm_provider: str = "nvidia"  # nvidia | ollama | litellm | openai
    llm_model: str = ""
    llm_base_url: str = ""
    llm_api_key: str = ""
    nvidia_api_key: str = ""
    openai_api_key: str = ""
    litellm_api_key: str = ""

    # --- Memory: empty REDIS_URL means "keep conversation history in process memory" ---
    redis_url: str = ""
    memory_ttl_seconds: int = 3600
    memory_max_messages: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
