import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from calculator_agent.config import Settings
from calculator_agent.llm import resolve_llm_config
from calculator_agent.security import BearerTokenMiddleware


def test_bearer_middleware():
    app = Starlette(
        routes=[Route("/secret", lambda r: PlainTextResponse("ok")), Route("/.well-known/card", lambda r: PlainTextResponse("card"))],
        middleware=[Middleware(BearerTokenMiddleware, token="t")],
    )
    client = TestClient(app)
    assert client.get("/secret").status_code == 401
    assert client.get("/secret", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert client.get("/secret", headers={"Authorization": "Bearer t"}).status_code == 200
    assert client.get("/.well-known/card").status_code == 200  # public


def test_nvidia_preset():
    config = resolve_llm_config(Settings(llm_provider="nvidia", nvidia_api_key="k", _env_file=None))
    assert config.base_url == "https://integrate.api.nvidia.com/v1"
    assert config.api_key == "k"


def test_ollama_needs_no_key_and_overrides_work():
    config = resolve_llm_config(Settings(llm_provider="ollama", llm_model="qwen2.5", _env_file=None))
    assert config.model == "qwen2.5"
    assert config.base_url.endswith(":11434/v1")


def test_missing_key_and_unknown_provider():
    with pytest.raises(RuntimeError, match="NVIDIA_API_KEY"):
        resolve_llm_config(Settings(llm_provider="nvidia", nvidia_api_key="", _env_file=None))
    with pytest.raises(ValueError, match="Unknown"):
        resolve_llm_config(Settings(llm_provider="nope", _env_file=None))
