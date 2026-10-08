"""MCP server -> REST API wired in-process (no sockets), plus the LLM agent with a fake model."""

import json
from types import SimpleNamespace

import httpx
import pytest
from fastmcp import Client

from calculator_agent.agents.calculator_agent import CalculatorAgent
from calculator_agent.agents.mcp_client import McpCalculator
from calculator_agent.agents.offline import parse_question
from calculator_agent.api.main import app as api_app
from calculator_agent.mcp_server import server
from calculator_agent.memory import InMemoryStore


@pytest.fixture(autouse=True)
def mcp_talks_to_api_in_process(monkeypatch):
    def fake_http():
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=api_app), base_url="http://api", headers={"X-API-Key": "test-key"}
        )

    monkeypatch.setattr(server, "_http", fake_http)


async def test_mcp_lists_tools_resource_and_prompt():
    async with Client(server.mcp) as client:
        assert {t.name for t in await client.list_tools()} == {"add", "subtract", "multiply", "divide"}
        assert "divide" in (await client.read_resource("calculator://help"))[0].text
        assert (await client.list_prompts())[0].name == "explain_calculation"


async def test_mcp_tool_calls_the_api():
    assert await McpCalculator(server.mcp).call("multiply", {"a": 6, "b": 7}) == 42


async def test_mcp_divide_by_zero_surfaces_api_message():
    with pytest.raises(RuntimeError, match="zero"):
        await McpCalculator(server.mcp).call("divide", {"a": 1, "b": 0})


async def test_mcp_tools_convert_to_openai_format():
    tools = await McpCalculator(server.mcp).openai_tools()
    assert {t["function"]["name"] for t in tools} == {"add", "subtract", "multiply", "divide"}
    assert tools[0]["function"]["parameters"]["type"] == "object"


class FakeLLM:
    """Asks for one tool call, then answers using the tool output. Records what it was sent."""

    def __init__(self):
        self.seen = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    async def _create(self, model, messages, tools):
        self.seen.append(list(messages))
        last = messages[-1]
        if isinstance(last, dict) and last["role"] == "tool":
            msg = SimpleNamespace(content=f"The answer is {last['content']}.", tool_calls=None)
        else:
            call = SimpleNamespace(
                id="c1", function=SimpleNamespace(name="multiply", arguments=json.dumps({"a": 6, "b": 7}))
            )
            msg = SimpleNamespace(content=None, tool_calls=[call])
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


async def test_agent_uses_tool_and_remembers_conversation():
    llm, memory = FakeLLM(), InMemoryStore()
    agent = CalculatorAgent(mcp=McpCalculator(server.mcp), memory=memory, llm=llm, model="fake")
    assert await agent.run("6 times 7?", session_id="s") == "The answer is 42.0."
    assert await agent.run("again", session_id="s") == "The answer is 42.0."
    # Second run's first LLM call includes the first turn from memory.
    second_call_messages = llm.seen[2]
    assert {"role": "user", "content": "6 times 7?"} in second_call_messages
    assert len(await memory.history("s")) == 4


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("What is 6 times 7?", ("multiply", 6, 7)),
        ("10 minus 4", ("subtract", 10, 4)),
        ("9 divided by 3", ("divide", 9, 3)),
        ("2 plus 2", ("add", 2, 2)),
    ],
)
def test_offline_parser(text, expected):
    assert parse_question(text) == expected


def test_offline_parser_rejects_nonsense():
    with pytest.raises(ValueError):
        parse_question("hello")
