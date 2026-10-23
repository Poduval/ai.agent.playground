import pytest

from calculator.config import get_settings as calculator_settings


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """Deterministic settings; env vars beat any local .env file."""
    monkeypatch.setenv("CALCULATOR_API_KEY", "test-key")
    calculator_settings.cache_clear()
    yield
    calculator_settings.cache_clear()
