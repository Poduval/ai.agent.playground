# Services

Part of the [AI Agent Playground](../README.md). A home for small REST APIs (FastAPI), each shipped with an **MCP server** so any agent can use it as tools straight away.

```text
 Agent (any project) ──MCP──►  <service>/mcp  ──HTTP + X-API-Key──►  <service>/api  (FastAPI)
```

| Service | What it does | API | MCP |
|---|---|---|---|
| [calculator](calculator/) | add, subtract, multiply, divide | `:8000` (`/docs`) | `:8001/mcp` |

Agents never import from here; they connect to a service's MCP URL (e.g. [agents/calculator](../agents/calculator/) uses `http://127.0.0.1:8001/mcp`).

## Quick start

```bash
cd services
make install                  # creates .venv, installs the package + dev tools
make calculator-api           # terminal 1: http://127.0.0.1:8000/docs (header X-API-Key: dev-api-key)
make calculator-mcp           # terminal 2: http://127.0.0.1:8001/mcp
make test && make lint        # offline, no servers needed
```

## Layout of one service

```text
calculator/
  config.py     settings (env vars: API key, API URL for the MCP server)
  api/          main.py routes, operations.py logic, schemas.py models
  mcp/server.py FastMCP tools that call the API; optional resource + prompt
common/         config base + API-key auth, shared by all services
tests/          test_<service>_api.py, test_<service>_mcp.py
```

## Adding a service

Use the `new-service` skill, or by hand: copy `calculator/` to `<name>/`, rename, give it the next free port pair (calculator 8000/8001, next 8010/8011, ...), add `<name>-api` / `<name>-mcp` console scripts and Makefile targets, register the package in `pyproject.toml`, add its env vars to `.env.example`, and add tests.

## Security notes

- The default key in `.env.example` is for localhost only. Servers bind to `127.0.0.1`.
- The MCP endpoints are unauthenticated in this template; add FastMCP auth before exposing them.

License: see the repository [LICENSE](../LICENSE).
