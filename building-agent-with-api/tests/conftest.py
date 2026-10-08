import pytest

from calculator_agent.config import get_settings


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """Deterministic settings; env vars beat any local .env file."""
    for name, value in {
        "CALCULATOR_API_KEY": "test-key",
        "A2A_BEARER_TOKEN": "test-token",
        "REDIS_URL": "",
        "LLM_PROVIDER": "nvidia",
        "LLM_MODEL": "",
        "LLM_BASE_URL": "",
        "LLM_API_KEY": "",
        "NVIDIA_API_KEY": "nv-test",
    }.items():
        monkeypatch.setenv(name, value)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
