import pytest

from agent.config import get_settings as agent_settings
from common.config import get_settings as common_settings


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """Deterministic settings; env vars beat any local .env file."""
    for name, value in {
        "A2A_BEARER_TOKEN": "test-token",
        "MCP_SERVERS": "calculator=http://127.0.0.1:8001/mcp",
        "AGENT_NAME": "Assistant",
        "REDIS_URL": "",
        "LLM_PROVIDER": "nvidia",
        "LLM_MODEL": "",
        "LLM_BASE_URL": "",
        "LLM_API_KEY": "",
        "NVIDIA_API_KEY": "nv-test",
    }.items():
        monkeypatch.setenv(name, value)
    for settings in (common_settings, agent_settings):
        settings.cache_clear()
    yield
    for settings in (common_settings, agent_settings):
        settings.cache_clear()
