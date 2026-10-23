# Architecture

## Request flow

1. `agent "6 times 7"` → `Agent.run` (or, with `--a2a`, `a2a.client.ask_agent` → A2A server → `ToolAgentExecutor`).
2. The agent loads the session's history from the memory store and asks every server in `MCP_SERVERS` for its tools (`list_tools`).
3. The LLM replies with a tool call (`calculator_multiply {a: 6, b: 7}`; names are `<server>_<tool>`); the agent runs it through the MCP client.
4. The MCP tool (in `../../services`) calls `POST /multiply` on the REST API with `X-API-Key`.
5. The result flows back; the LLM writes the final sentence; user + assistant turns are saved to memory.

## Modules

`common/` is shared by any agent; `agent/` is the agent built on it. The REST API and MCP server live in the root [services](../../../services/) project; see its README for those modules.

| Module | Responsibility |
|---|---|
| `common/config.py` | Base `Settings` (pydantic-settings): LLM, memory, A2A token |
| `common/llm/client.py` | Provider presets → `AsyncOpenAI` client |
| `common/memory/store.py` | `MemoryStore` protocol, `InMemoryStore`, `RedisStore` |
| `common/security/auth.py` | `BearerTokenMiddleware` |
| `common/mcp_client.py` | List/call tools on one or more MCP servers (prefixed names); converts schemas to OpenAI format |
| `agent/config.py` | `AgentSettings`: name, instructions, `MCP_SERVERS`, A2A URL |
| `agent/main.py` | Tool-calling loop (max 5 steps) + memory |
| `agent/a2a/card.py` | Agent Card: one skill per MCP server, modes, bearer security scheme |
| `agent/a2a/executor.py` | Task lifecycle; runs the agent |
| `agent/a2a/server.py` / `client.py` | Starlette app with auth middleware / authenticated client |
| `agent/cli.py` | `agent` command (ask, `--tools`, `--call`, `--a2a`) |

## Ports

A2A 8002 here · API 8000 and MCP 8001 (`/mcp`) in services · Redis 6379 · LiteLLM 4000 · Ollama 11434

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

- New operation: add it in `services/calculator` (`api/operations.py` and a tool in `mcp/server.py`); tools are discovered automatically by the agent.
- New tools: add a service in `../../services`, then add it to `MCP_SERVERS`. A different agent: add a folder under `agents/` ([docs/new-agent.md](../../../docs/new-agent.md)).
- New provider: add a preset in `common/llm/client.py`.
- New memory backend: implement the `MemoryStore` protocol in `common/memory/`.
- Persistent A2A tasks: replace `InMemoryTaskStore` in `agent/a2a/server.py`.
