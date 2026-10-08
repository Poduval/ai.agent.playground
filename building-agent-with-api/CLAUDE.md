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
common/                shared by every agent; knows nothing about calculators
  config.py            base Settings (LLM, memory, A2A token)
  llm/client.py        provider presets (nvidia, ollama, litellm, openai) -> AsyncOpenAI
  memory/store.py      InMemoryStore | RedisStore (REDIS_URL)
  security/auth.py     api_key_auth(key_getter), BearerTokenMiddleware
  mcp_client.py        McpClient(target): list tools (OpenAI format), call tools
calculator/            one agent (copy this folder to add another)
  config.py            CalculatorSettings(Settings): URLs + API key
  api/                 FastAPI calculator (add/subtract/multiply/divide), X-API-Key
  mcp/server.py        FastMCP tools calling the API; resource + prompt
  agents/              main.py (tool loop + memory), offline.py (--demo parser)
  a2a/                 card (skills, bearer scheme), executor, server, client
  cli.py               `calculator-agent` command
tests/                 offline suite: test_common_*, test_calculator_*; conftest pins settings
deploy/litellm/        LiteLLM proxy config; docker-compose.yml has redis + litellm
```

Adding an agent: create a sibling package (e.g. `weather/`) with its own `config.py` (subclass `common.config.Settings`), api, mcp, agents, a2a; reuse `common/`; add console scripts and ports; register the package in `pyproject.toml`.

## Gotchas

- `calculator.a2a` and `calculator.mcp` share names with the `a2a` and `mcp` SDKs. Imports are absolute, so `from a2a...` / `import mcp` are always the SDKs; never add top-level `a2a.py`/`mcp.py` modules or relative imports that could shadow them.
- Tests replace `calculator.mcp.server._http` to route MCP→API in-process; keep that seam when refactoring.
- `fastmcp` is pinned and `a2a-sdk` bounded `<2`; check the SDK source in `.venv` when APIs differ from memory.
- The real-LLM path (NVIDIA/Ollama) is not covered by automated tests; they use a fake LLM.
- Default dev secrets (`dev-api-key`, `dev-a2a-token`) are localhost-only.
