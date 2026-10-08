# Architecture

## Request flow

1. `calculator-agent "6 times 7"` → `CalculatorAgent.run` (or, with `--a2a`, `a2a.client.ask_agent` → A2A server → `CalculatorExecutor`).
2. The agent loads the session's history from the memory store and asks the MCP server for its tools (`list_tools`).
3. The LLM replies with a tool call (`multiply {a: 6, b: 7}`); the agent runs it through the MCP client.
4. The MCP tool calls `POST /multiply` on the REST API with `X-API-Key`.
5. The result flows back; the LLM writes the final sentence; user + assistant turns are saved to memory.

## Modules

`common/` is shared by any agent; `calculator/` is one agent built on it.

| Module | Responsibility |
|---|---|
| `common/config.py` | Base `Settings` (pydantic-settings): LLM, memory, A2A token |
| `common/llm/client.py` | Provider presets → `AsyncOpenAI` client |
| `common/memory/store.py` | `MemoryStore` protocol, `InMemoryStore`, `RedisStore` |
| `common/security/auth.py` | `api_key_auth` dependency factory, `BearerTokenMiddleware` |
| `common/mcp_client.py` | List/call MCP tools; converts schemas to OpenAI format |
| `calculator/config.py` | `CalculatorSettings`: service URLs and API key |
| `calculator/api/` | `main.py` routes, `operations.py` pure math, `schemas.py` models |
| `calculator/mcp/server.py` | FastMCP: 4 tools, `calculator://help` resource, `explain_calculation` prompt |
| `calculator/agents/main.py` | Tool-calling loop (max 5 steps) + memory |
| `calculator/agents/offline.py` | Rule-based parser for `--demo` |
| `calculator/a2a/card.py` | Agent Card: skills, modes, bearer security scheme |
| `calculator/a2a/executor.py` | Task lifecycle; JSON → direct MCP call, text → LLM agent |
| `calculator/a2a/server.py` / `client.py` | Starlette app with auth middleware / authenticated client |
| `calculator/cli.py` | `calculator-agent` command |

## Ports

API 8000 · MCP 8001 (`/mcp`) · A2A 8002 · Redis 6379 · LiteLLM 4000 · Ollama 11434

## Security model

| Boundary | Protection |
|---|---|
| Client → REST API | `X-API-Key` (constant-time compare); `/health` is public |
| MCP server → REST API | Forwards the API key from config |
| Client → A2A | `Authorization: Bearer`, declared in the Agent Card; the card is public |
| Inputs | Pydantic validation, NaN/Infinity rejected, divide-by-zero → 400 |
| LLM output | Tool arguments are validated by the MCP tool schema and REST API |
| MCP endpoint | **Not authenticated** here (localhost only). Add FastMCP auth before exposing it |
| Secrets | Only via env / `.env` (gitignored) |

## Extending

- New operation: add to `api/operations.py` and a tool in `mcp/server.py`; tools are discovered automatically by the agent.
- New agent: add a sibling package next to `calculator/` and reuse `common/` (see CLAUDE.md).
- New provider: add a preset in `common/llm/client.py`.
- New memory backend: implement the `MemoryStore` protocol in `common/memory/`.
- Persistent A2A tasks: replace `InMemoryTaskStore` in `calculator/a2a/server.py`.
