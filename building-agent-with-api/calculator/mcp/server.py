"""FastMCP server. Tools call the REST API over HTTP, forwarding the API key.

Run: `calculator-mcp`  (Streamable HTTP on http://127.0.0.1:8001/mcp)
"""

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from calculator.config import get_settings

mcp = FastMCP("Calculator", instructions="Basic arithmetic on two numbers.")


def _http() -> httpx.AsyncClient:
    """Build the HTTP client for the REST API (tests replace this function)."""
    settings = get_settings()
    return httpx.AsyncClient(
        base_url=settings.api_url,
        headers={"X-API-Key": settings.calculator_api_key},
        timeout=10,
    )


async def _call_api(operation: str, a: float, b: float) -> float:
    async with _http() as client:
        response = await client.post(f"/{operation}", json={"a": a, "b": b})
    if response.status_code == 400:  # business error, e.g. divide by zero
        raise ToolError(response.json()["detail"])
    response.raise_for_status()
    return response.json()["result"]


# --- Tools: actions the model can invoke -------------------------------------
@mcp.tool
async def add(a: float, b: float) -> float:
    """Add two numbers."""
    return await _call_api("add", a, b)


@mcp.tool
async def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return await _call_api("subtract", a, b)


@mcp.tool
async def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return await _call_api("multiply", a, b)


@mcp.tool
async def divide(a: float, b: float) -> float:
    """Divide a by b. Fails if b is zero."""
    return await _call_api("divide", a, b)


# --- Resource: read-only context the client can load -------------------------
@mcp.resource("calculator://help")
def help_text() -> str:
    """Describe the available operations."""
    return "Operations: add, subtract, multiply, divide. Each takes numbers a and b."


# --- Prompt: a reusable prompt template --------------------------------------
@mcp.prompt
def explain_calculation(expression: str) -> str:
    """Ask the model to solve and explain an arithmetic expression using the tools."""
    return f"Use the calculator tools to solve '{expression}' and explain each step briefly."


def main() -> None:
    mcp.run(transport="http", host="127.0.0.1", port=8001)


if __name__ == "__main__":
    main()
