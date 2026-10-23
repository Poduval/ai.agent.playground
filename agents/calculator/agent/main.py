"""An LLM agent: the model decides which MCP tool to call, we run it, repeat until answered.

This loop is the heart of "tool calling" - read it top to bottom.
"""

import json

from agent.config import get_settings
from common.llm import get_llm_client, resolve_llm_config
from common.mcp_client import McpClient
from common.memory import MemoryStore, get_store

MAX_STEPS = 5  # safety limit so a confused model cannot loop forever


class Agent:
    def __init__(self, mcp: McpClient | None = None, memory: MemoryStore | None = None, llm=None, model: str | None = None):
        self.settings = get_settings()
        self.mcp = mcp or McpClient(self.settings.mcp_server_urls)
        self.memory = memory or get_store()
        if llm is None:
            config = resolve_llm_config()
            llm, model = get_llm_client(config), model or config.model
        self.llm, self.model = llm, model

    async def run(self, question: str, session_id: str = "default") -> str:
        tools = await self.mcp.openai_tools()  # discovered from the MCP server, not hardcoded
        messages = [
            {"role": "system", "content": self.settings.agent_instructions},
            *await self.memory.history(session_id),  # earlier turns of this conversation
            {"role": "user", "content": question},
        ]
        for _ in range(MAX_STEPS):
            reply = (await self.llm.chat.completions.create(model=self.model, messages=messages, tools=tools)).choices[0].message
            if not reply.tool_calls:
                answer = reply.content or ""
                await self.memory.append(session_id, "user", question)
                await self.memory.append(session_id, "assistant", answer)
                return answer
            messages.append(reply)
            for call in reply.tool_calls:
                try:
                    output = json.dumps(await self.mcp.call(call.function.name, json.loads(call.function.arguments)))
                except Exception as exc:  # report tool errors to the model so it can respond sensibly
                    output = f"Error: {exc}"
                messages.append({"role": "tool", "tool_call_id": call.id, "content": output})
        raise RuntimeError(f"No final answer after {MAX_STEPS} steps.")
