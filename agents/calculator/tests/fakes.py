"""Offline stand-ins: a calculator MCP server (the real one lives in ../../services) and a scripted LLM."""

import json
from types import SimpleNamespace

from fastmcp import FastMCP

fake_mcp = FastMCP("FakeCalculator")


@fake_mcp.tool
def add(a: float, b: float) -> float:
    return a + b


@fake_mcp.tool
def multiply(a: float, b: float) -> float:
    return a * b


@fake_mcp.tool
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


class FakeLLM:
    """Asks for one tool call, then answers using the tool output. Records what it was sent."""

    def __init__(self, tool="calculator_multiply", arguments=None):
        self.seen = []
        self.tool, self.arguments = tool, arguments or {"a": 6, "b": 7}
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    async def _create(self, model, messages, tools):
        self.seen.append(list(messages))
        last = messages[-1]
        if isinstance(last, dict) and last["role"] == "tool":
            msg = SimpleNamespace(content=f"The answer is {last['content']}.", tool_calls=None)
        else:
            call = SimpleNamespace(id="c1", function=SimpleNamespace(name=self.tool, arguments=json.dumps(self.arguments)))
            msg = SimpleNamespace(content=None, tool_calls=[call])
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])
