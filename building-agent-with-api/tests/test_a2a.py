"""Full A2A round trip in-process: Agent Card discovery, bearer auth, task execution."""

import json

import httpx
import pytest
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_stream_response_text, new_text_message
from a2a.types import Role, SendMessageRequest

from calculator_agent.a2a.card import build_agent_card
from calculator_agent.a2a.executor import CalculatorExecutor
from calculator_agent.a2a.server import build_app
from calculator_agent.agents.mcp_client import McpCalculator
from calculator_agent.api.main import app as api_app
from calculator_agent.mcp_server import server


@pytest.fixture
def a2a_app(monkeypatch):
    monkeypatch.setattr(
        server,
        "_http",
        lambda: httpx.AsyncClient(
            transport=httpx.ASGITransport(app=api_app), base_url="http://api", headers={"X-API-Key": "test-key"}
        ),
    )
    return build_app(executor=CalculatorExecutor(mcp=McpCalculator(server.mcp)))


def _http(app, token: str | None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://agent", headers=headers)


def test_card_describes_skills_and_security():
    card = build_agent_card()
    assert {s.id for s in card.skills} == {"structured-arithmetic", "natural-language-math"}
    assert "bearer" in card.security_schemes


async def test_card_is_public_but_rpc_requires_token(a2a_app):
    async with _http(a2a_app, None) as http:
        assert (await http.get("/.well-known/agent-card.json")).status_code == 200
        assert (await http.post("/", json={})).status_code == 401


async def test_structured_request_round_trip(a2a_app):
    async with _http(a2a_app, "test-token") as http:
        client = await create_client("http://agent", ClientConfig(httpx_client=http, streaming=False))
        message = new_text_message(text=json.dumps({"operation": "divide", "a": 84, "b": 2}), role=Role.ROLE_USER)
        texts = [get_stream_response_text(e) async for e in client.send_message(SendMessageRequest(message=message))]
    assert json.loads(next(t for t in texts if t)) == {"operation": "divide", "result": 42}


async def test_failure_is_reported_not_raised(a2a_app):
    async with _http(a2a_app, "test-token") as http:
        client = await create_client("http://agent", ClientConfig(httpx_client=http, streaming=False))
        message = new_text_message(text=json.dumps({"operation": "divide", "a": 1, "b": 0}), role=Role.ROLE_USER)
        events = [e async for e in client.send_message(SendMessageRequest(message=message))]
    assert "FAILED" in str(events[-1])
