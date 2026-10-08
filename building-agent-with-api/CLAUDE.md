# building-agent-with-api

FastAPI calculator → MCP server → LLM tool-calling agent (+ memory) → A2A agent, with auth. See [README.md](README.md) and [docs/architecture.md](docs/architecture.md).

## Commands (run from this folder; Python ≥3.11, venv at `.venv`)

```bash
make install        # venv + editable install with dev extras
make test           # pytest, fully offline (33 tests)
make lint           # ruff
make api | mcp | a2a    # services (separate terminals): :8000, :8001/mcp, :8002
make redis | litellm    # optional docker services
.venv/bin/calculator-agent [--demo|--a2a] [--session ID] "question"
```

## Map

```
calculator_agent/
  config.py            Settings (env/.env) - single source of config
  api/                 FastAPI calculator (add/subtract/multiply/divide), X-API-Key
  mcp_server/server.py FastMCP tools calling the API; resource + prompt
  llm/client.py        provider presets (nvidia, ollama, litellm, openai) -> AsyncOpenAI
  agents/              mcp_client, calculator_agent (tool loop + memory), offline parser
  memory/store.py      InMemoryStore | RedisStore (REDIS_URL)
  a2a/                 card (skills, bearer scheme), executor, server, client
  security/auth.py     require_api_key, BearerTokenMiddleware
  cli.py               `calculator-agent` command
tests/                 offline suite; conftest pins test settings
deploy/litellm/        LiteLLM proxy config; docker-compose.yml has redis + litellm
```

## Gotchas

- `calculator_agent.a2a` shares a name with the `a2a` SDK. Imports are absolute, so `from a2a...` is always the SDK; never add an `a2a.py` module or relative imports that could shadow it.
- Tests replace `calculator_agent.mcp_server.server._http` to route MCP→API in-process; keep that seam when refactoring.
- `fastmcp` is pinned and `a2a-sdk` bounded `<2`; check the SDK source in `.venv` when APIs differ from memory.
- The real-LLM path (NVIDIA/Ollama) is not covered by automated tests; they use a fake LLM.
- Default dev secrets (`dev-api-key`, `dev-a2a-token`) are localhost-only.
