# services

FastAPI services, each with an MCP server so agents can call them as tools. See [README.md](README.md).

## Commands (run from this folder; Python ≥3.11, venv at `.venv`)

```bash
make install                      # venv + editable install with dev extras
make test | lint                  # offline
make calculator-api | calculator-mcp   # :8000, :8001/mcp (separate terminals)
```

## Map

```
common/                shared by every service; knows nothing about any one domain
  config.py            base Settings (reads .env)
  security/auth.py     api_key_auth(key_getter): FastAPI dependency for X-API-Key
calculator/            one service (copy this folder to add another)
  config.py            CalculatorSettings: API key, API URL for the MCP server
  api/                 FastAPI app (add/subtract/multiply/divide)
  mcp/server.py        FastMCP tools calling the API; resource + prompt
tests/                 test_<service>_api.py, test_<service>_mcp.py; conftest pins settings
```

Adding a service: use the `new-service` skill. One API + one MCP server per service, each pair on its own ports.

## Gotchas

- `calculator.mcp` shares its name with the `mcp` SDK. Imports are absolute; never add a top-level `mcp.py` or relative imports that could shadow it.
- Tests replace `calculator.mcp.server._http` to route MCP→API in-process; keep that seam.
- Never import from another project (e.g. agents); agents reach services only through MCP URLs.
- Default dev secret (`dev-api-key`) is localhost-only.
