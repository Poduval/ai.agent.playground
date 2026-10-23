"""MCP server -> REST API wired in-process (no sockets)."""

import httpx
import pytest
from fastmcp import Client

from calculator.api.main import app as api_app
from calculator.mcp import server


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
    async with Client(server.mcp) as client:
        result = await client.call_tool("multiply", {"a": 6, "b": 7})
    assert result.data == 42


async def test_mcp_divide_by_zero_surfaces_api_message():
    async with Client(server.mcp) as client:
        with pytest.raises(Exception, match="zero"):
            await client.call_tool("divide", {"a": 1, "b": 0})
