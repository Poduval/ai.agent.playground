"""Full A2A round trip in-process: Agent Card discovery, bearer auth, task execution."""

import httpx
import pytest
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_stream_response_text, new_text_message
from a2a.types import Role, SendMessageRequest

from agent.a2a.card import build_agent_card
from agent.a2a.executor import ToolAgentExecutor
from agent.a2a.server import build_app
from agent.main import Agent
from common.mcp_client import McpClient
from common.memory import InMemoryStore
from fakes import FakeLLM, fake_mcp


def _executor(llm):
    agent = Agent(mcp=McpClient({"calculator": fake_mcp}), memory=InMemoryStore(), llm=llm, model="fake")
    return ToolAgentExecutor(agent=agent)


@pytest.fixture
def a2a_app():
    return build_app(executor=_executor(FakeLLM()))


def _http(app, token: str | None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://agent", headers=headers)


def test_card_has_one_skill_per_mcp_server_and_bearer_security():
    card = build_agent_card()
    assert [s.id for s in card.skills] == ["calculator"]
    assert "bearer" in card.security_schemes


async def test_card_is_public_but_rpc_requires_token(a2a_app):
    async with _http(a2a_app, None) as http:
        assert (await http.get("/.well-known/agent-card.json")).status_code == 200
        assert (await http.post("/", json={})).status_code == 401


async def _ask(app, text="What is 6 times 7?"):
    async with _http(app, "test-token") as http:
        client = await create_client("http://agent", ClientConfig(httpx_client=http, streaming=False))
        message = new_text_message(text=text, role=Role.ROLE_USER)
        return [e async for e in client.send_message(SendMessageRequest(message=message))]


async def test_text_request_round_trip(a2a_app):
    events = await _ask(a2a_app)
    assert "The answer is 42.0." in [get_stream_response_text(e) for e in events]


async def test_failure_is_reported_not_raised():
    app = build_app(executor=_executor(FakeLLM(tool="calculator_divide", arguments={"a": 1, "b": 0})))
    events = await _ask(app)
    assert "The answer is Error" in str([get_stream_response_text(e) for e in events])  # tool error is relayed to the model
