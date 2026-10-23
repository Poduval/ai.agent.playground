"""Calculator service settings."""

from functools import lru_cache

from common.config import Settings


class CalculatorSettings(Settings):
    # --- Where the MCP server finds its REST API ---
    calculator_api_url: str = "http://127.0.0.1:8000"

    # --- Security ---
    calculator_api_key: str = "dev-api-key"  # REST API expects this in `X-API-Key`


@lru_cache
def get_settings() -> CalculatorSettings:
    return CalculatorSettings()
