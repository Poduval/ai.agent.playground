---
name: new-service
description: Add a new FastAPI service with its MCP server (e.g. weather/) to services/ by copying the calculator/ pattern. Use when asked to add an API, a tool service, or an MCP server for agents.
---
Work inside `services/`. Read its CLAUDE.md first.

1. Copy `calculator/` to `<name>/`; rename modules, classes, settings and the MCP resource/prompt names.
2. `<name>/config.py`: subclass `common.config.Settings` with `<name>_api_key`, `<name>_api_url`. Config only via settings; add every env var to `.env.example` and the README.
3. `<name>/api/`: FastAPI app, `X-API-Key` via `common.security.api_key_auth`, `/health` public, validated schemas. `<name>/mcp/server.py`: FastMCP tools that call the API through a replaceable `_http()` seam.
4. Pick the next free port pair (calculator 8000/8001, then 8010/8011, 8020/8021 ...); bind 127.0.0.1.
5. Register the package in `pyproject.toml` (`packages`, console scripts `<name>-api`, `<name>-mcp`) and add Makefile targets and `.PHONY` entries; extend the lint path.
6. Add `tests/test_<name>_api.py` and `tests/test_<name>_mcp.py` (in-process via `httpx.ASGITransport`, offline).
7. Run the `verify` skill in `services/`, add the service to the table in `services/README.md` and the map in `services/CLAUDE.md`, then add a RELEASE.md entry (`release-entry`).
8. To let an agent use it, add `name=url` to that agent's `MCP_SERVERS`; never import from `services/` in an agent project. If the agent has tests, add a stand-in MCP server to its `tests/`.
