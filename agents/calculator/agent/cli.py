"""Command line entry point: `agent "What is 6 times 7?"`."""

import argparse
import asyncio
import json
import sys

from agent.config import get_settings
from agent.main import Agent
from common.mcp_client import McpClient


async def _run(args: argparse.Namespace) -> str:
    mcp = McpClient(get_settings().mcp_server_urls)
    if args.tools:  # no LLM: show what the MCP servers offer
        return "\n".join(f"{server}_{tool.name}: {tool.description}" for server, tool in await mcp.tools())
    if args.call:  # no LLM: call one tool directly, e.g. --call calculator_add --args '{"a": 1, "b": 2}'
        return json.dumps(await mcp.call(args.call, json.loads(args.args)))
    if not args.question:
        raise ValueError("Give a question, or use --tools / --call.")
    if args.a2a:  # go through the A2A agent over the network
        from agent.a2a.client import ask_agent

        return await ask_agent(args.question, context_id=args.session)
    return await Agent(mcp=mcp).run(args.question, session_id=args.session)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the agent a question; it uses the MCP servers in MCP_SERVERS.")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--a2a", action="store_true", help="route through the A2A agent")
    parser.add_argument("--tools", action="store_true", help="list the MCP tools (no LLM needed)")
    parser.add_argument("--call", metavar="TOOL", help="call one MCP tool directly (no LLM needed)")
    parser.add_argument("--args", default="{}", help="JSON arguments for --call")
    parser.add_argument("--session", default="cli", help="conversation id used for memory")
    args = parser.parse_args()
    try:
        print(asyncio.run(_run(args)))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
