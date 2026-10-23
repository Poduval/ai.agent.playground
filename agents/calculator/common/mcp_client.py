"""Thin wrapper around the FastMCP client: list tools, call tools, friendly errors.

Talks to one or more MCP servers. Tool names are prefixed with the server name
(`calculator_add`) so tools from different servers can never collide.
"""

from typing import Any

from fastmcp import Client


def _leaf_errors(error: BaseException) -> list[BaseException]:
    """FastMCP may wrap the real error in an exception group; unwrap it."""
    if isinstance(error, BaseExceptionGroup):
        return [leaf for child in error.exceptions for leaf in _leaf_errors(child)]
    return [error]


class McpClient:
    """`servers` maps a name to a URL (normal use) or a FastMCP server object (in-memory tests)."""

    def __init__(self, servers: dict[str, Any]):
        self.servers = servers

    def _wrap(self, exc: Exception, target: Any) -> RuntimeError:
        leaves = _leaf_errors(exc)
        if any(type(e).__name__ == "ConnectError" for e in leaves):
            return RuntimeError(f"Cannot reach the MCP server at {target}. Is it running?")
        return RuntimeError("; ".join(str(e) for e in leaves))

    async def tools(self) -> list[tuple[str, Any]]:
        """(server name, MCP tool) for every tool on every server."""
        found = []
        for name, target in self.servers.items():
            try:
                async with Client(target) as client:
                    found += [(name, tool) for tool in await client.list_tools()]
            except Exception as exc:
                raise self._wrap(exc, target) from exc
        return found

    async def openai_tools(self) -> list[dict]:
        """MCP tool definitions converted to the OpenAI `tools` format."""
        return [
            {
                "type": "function",
                "function": {"name": f"{server}_{t.name}", "description": t.description or "", "parameters": t.input_schema},
            }
            for server, t in await self.tools()
        ]

    async def call(self, name: str, arguments: dict) -> Any:
        """Call a prefixed tool name such as `calculator_add`."""
        server = next((s for s in self.servers if name.startswith(f"{s}_")), None)
        if server is None:
            raise RuntimeError(f"Unknown tool '{name}'. Known servers: {', '.join(self.servers)}")
        target = self.servers[server]
        try:
            async with Client(target) as client:
                result = await client.call_tool(name.removeprefix(f"{server}_"), arguments, raise_on_error=False)
        except Exception as exc:
            raise self._wrap(exc, target) from exc
        if result.is_error:
            raise RuntimeError("; ".join(getattr(c, "text", "") for c in result.content))
        content = result.structured_content
        if isinstance(content, dict) and set(content) == {"result"}:  # FastMCP wraps non-object returns
            return content["result"]
        return content if content is not None else "".join(getattr(c, "text", "") for c in result.content)
