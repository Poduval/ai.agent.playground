"""Command line entry point: `calculator-agent "What is 6 times 7?"`."""

import argparse
import asyncio
import sys

from calculator.agents.main import CalculatorAgent
from calculator.agents.offline import parse_question
from calculator.config import get_settings
from common.mcp_client import McpClient


async def _ask(args: argparse.Namespace) -> str:
    if args.demo:  # no LLM: parse with rules, call the MCP tool directly
        operation, a, b = parse_question(args.question)
        result = await McpClient(get_settings().mcp_url).call(operation, {"a": a, "b": b})
        return f"{a:g} {operation} {b:g} = {result:g}  (demo mode, no LLM)"
    if args.a2a:  # go through the A2A agent over the network
        from calculator.a2a.client import ask_agent

        return await ask_agent(args.question, context_id=args.session)
    return await CalculatorAgent().run(args.question, session_id=args.session)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the calculator agent a question.")
    parser.add_argument("question")
    parser.add_argument("--a2a", action="store_true", help="route through the A2A agent")
    parser.add_argument("--demo", action="store_true", help="skip the LLM; use a simple rule-based parser")
    parser.add_argument("--session", default="cli", help="conversation id used for memory")
    args = parser.parse_args()
    try:
        print(asyncio.run(_ask(args)))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
