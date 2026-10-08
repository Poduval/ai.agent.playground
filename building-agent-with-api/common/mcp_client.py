"""Thin wrapper around the FastMCP client: list tools, call tools, friendly errors."""

from typing import Any

from fastmcp import Client


def _leaf_errors(error: BaseException) -> list[BaseException]:
    """FastMCP may wrap the real error in an exception group; unwrap it."""
    if isinstance(error, BaseExceptionGroup):
        return [leaf for child in error.exceptions for leaf in _leaf_errors(child)]
    return [error]


class McpClient:
    """`target` is a URL (normal use) or a FastMCP server object (in-memory tests)."""

    def __init__(self, target: Any):
        self.target = target

    def _wrap(self, exc: Exception) -> RuntimeError:
        leaves = _leaf_errors(exc)
        if any(type(e).__name__ == "ConnectError" for e in leaves):
            return RuntimeError(f"Cannot reach the MCP server at {self.target}. Is it running?")
        return RuntimeError("; ".join(str(e) for e in leaves))

    async def openai_tools(self) -> list[dict]:
        """MCP tool definitions converted to the OpenAI `tools` format."""
        try:
            async with Client(self.target) as client:
                tools = await client.list_tools()
        except Exception as exc:
            raise self._wrap(exc) from exc
        return [
            {"type": "function", "function": {"name": t.name, "description": t.description or "", "parameters": t.input_schema}}
            for t in tools
        ]

    async def call(self, name: str, arguments: dict) -> float:
        try:
            async with Client(self.target) as client:
                result = await client.call_tool(name, arguments, raise_on_error=False)
        except Exception as exc:
            raise self._wrap(exc) from exc
        if result.is_error:
            raise RuntimeError("; ".join(getattr(c, "text", "") for c in result.content))
        content = result.structured_content
        return content["result"] if isinstance(content, dict) else content
