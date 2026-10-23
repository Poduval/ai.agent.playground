"""The agent loop and MCP client, using the stand-ins from fakes.py."""

import pytest

from agent.config import AgentSettings
from agent.main import Agent
from common.mcp_client import McpClient
from common.memory import InMemoryStore
from fakes import FakeLLM, fake_mcp

SERVERS = {"calculator": fake_mcp}


def test_mcp_servers_setting_parses_name_url_pairs():
    settings = AgentSettings(mcp_servers="a=http://x/mcp, b=http://y/mcp", _env_file=None)
    assert settings.mcp_server_urls == {"a": "http://x/mcp", "b": "http://y/mcp"}


async def test_tools_are_prefixed_with_the_server_name_in_openai_format():
    tools = await McpClient(SERVERS).openai_tools()
    assert {t["function"]["name"] for t in tools} == {"calculator_add", "calculator_multiply", "calculator_divide"}
    assert tools[0]["function"]["parameters"]["type"] == "object"


async def test_tools_from_several_servers_do_not_collide():
    names = {t["function"]["name"] for t in await McpClient({"one": fake_mcp, "two": fake_mcp}).openai_tools()}
    assert {"one_add", "two_add"} <= names


async def test_call_tool_surfaces_errors_and_unknown_names():
    client = McpClient(SERVERS)
    assert await client.call("calculator_multiply", {"a": 6, "b": 7}) == 42
    with pytest.raises(RuntimeError, match="zero"):
        await client.call("calculator_divide", {"a": 1, "b": 0})
    with pytest.raises(RuntimeError, match="Unknown tool"):
        await client.call("weather_now", {})


async def test_agent_uses_tool_and_remembers_conversation():
    llm, memory = FakeLLM(), InMemoryStore()
    agent = Agent(mcp=McpClient(SERVERS), memory=memory, llm=llm, model="fake")
    assert await agent.run("6 times 7?", session_id="s") == "The answer is 42.0."
    assert await agent.run("again", session_id="s") == "The answer is 42.0."
    # Second run's first LLM call includes the first turn from memory.
    second_call_messages = llm.seen[2]
    assert {"role": "user", "content": "6 times 7?"} in second_call_messages
    assert len(await memory.history("s")) == 4


async def test_system_prompt_comes_from_settings(monkeypatch):
    monkeypatch.setenv("AGENT_INSTRUCTIONS", "Be brief.")
    from agent.config import get_settings

    get_settings.cache_clear()
    llm = FakeLLM()
    await Agent(mcp=McpClient(SERVERS), memory=InMemoryStore(), llm=llm, model="fake").run("hi")
    assert llm.seen[0][0] == {"role": "system", "content": "Be brief."}
