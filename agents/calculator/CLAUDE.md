# calculator agent

Basis: API (tools from the calculator service over MCP). LLM tool-calling agent (+ memory) → A2A agent, using the calculator MCP server from `../../services`, with auth. See [README.md](README.md) and [docs/architecture.md](docs/architecture.md).

## Commands (run from this folder; Python ≥3.11, venv at `.venv`)

```bash
make install        # venv + editable install with dev extras
make test           # pytest, fully offline (21 tests)
make lint           # ruff
make a2a            # A2A server :8002 (needs ../../services calculator-mcp on :8001)
make redis | litellm    # optional docker services
.venv/bin/agent [--a2a] [--session ID] "question"   # also: agent --tools | --call TOOL --args JSON
```

## Map

```
common/                shared by every agent; knows nothing about any one service
  config.py            base Settings (LLM, memory, A2A token)
  llm/client.py        provider presets (nvidia, ollama, litellm, openai) -> AsyncOpenAI
  memory/store.py      InMemoryStore | RedisStore (REDIS_URL)
  security/auth.py     BearerTokenMiddleware
  mcp_client.py        McpClient({name: url}): list tools (OpenAI format, prefixed `name_tool`), call tools
agent/                 the generic agent (name/instructions/servers come from settings)
  config.py            AgentSettings(Settings): name, instructions, MCP_SERVERS, A2A URL
  main.py              Agent: tool loop + memory
  a2a/                 card (skills, bearer scheme), executor, server, client
  cli.py               `agent` command
tests/                 offline suite: test_common_*, test_agent_*; fakes.py stands in for MCP + LLM; conftest pins settings
deploy/litellm/        LiteLLM proxy config; docker-compose.yml has redis + litellm
```

The API and MCP server live in `../../services` (never import from it; reach it via `MCP_SERVERS`).

Another service for the agent: build it in `../../services` (`new-service` skill), then add `name=url` to `MCP_SERVERS`. A different agent: its own folder under `../` (see `../../docs/new-agent.md`); this one is not meant to be reused in place.

## Gotchas

- `agent.a2a` shares its name with the `a2a` SDK. Imports are absolute, so `from a2a...` is always the SDK; never add a top-level `a2a.py` module or relative imports that could shadow it.
- Tests use `tests/fakes.py` (fake MCP server + `FakeLLM`) instead of the real servers; keep its tool names/results in sync with `services/calculator`. Tool names are `<server>_<tool>`.
- `fastmcp` is pinned and `a2a-sdk` bounded `<2`; check the SDK source in `.venv` when APIs differ from memory.
- The real-LLM path (NVIDIA/Ollama) is not covered by automated tests; they use a fake LLM.
- Default dev secret (`dev-a2a-token`) is localhost-only.
