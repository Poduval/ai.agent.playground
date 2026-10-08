"""Calculator-specific settings on top of the shared ones in `common.config`."""

from functools import lru_cache

from common.config import Settings


class CalculatorSettings(Settings):
    # --- Service URLs (where each layer can be reached) ---
    api_url: str = "http://127.0.0.1:8000"
    mcp_url: str = "http://127.0.0.1:8001/mcp"
    a2a_url: str = "http://127.0.0.1:8002"

    # --- Security ---
    calculator_api_key: str = "dev-api-key"  # REST API expects this in `X-API-Key`


@lru_cache
def get_settings() -> CalculatorSettings:
    return CalculatorSettings()
