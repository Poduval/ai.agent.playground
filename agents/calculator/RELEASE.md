# Release Log: Calculator Agent

Per-release record of the whole agent: component versions, infrastructure, defaults and changes. Newest first. The repo-wide commit log is [../../RELEASE.md](../../RELEASE.md).

**How to cut a release**

1. Bump `__version__` in [agent/__init__.py](agent/__init__.py) and `version` in [pyproject.toml](pyproject.toml). The API (OpenAPI) version and the Agent Card version both read `__version__`.
2. Add a section below, copying the template at the bottom. Take dependency versions from `.venv/bin/pip list` after `make install`.
3. Run `make test` and `make lint` and record the results.

## Unreleased

- Moved from `building-agent-with-api/` to `agents/calculator/`; project renamed `calculator-agent`; README now starts with a Basis section.
- Moved the calculator REST API and MCP server to the new top-level [services](../../services/) project; this project keeps the agent, A2A and CLI and reaches MCP via `MCP_URL`.
- Removed `calculator-api`/`calculator-mcp` scripts, `make api`/`make mcp`, `API_URL`, `CALCULATOR_API_KEY`, `api_key_auth` and the `fastapi` dependency from this project.
- Tests now use `tests/fakes.py` (fake MCP server + scripted LLM) instead of the real MCP server.
- Renamed package `calculator/` to `agent/` and made it generic: `AGENT_NAME`, `AGENT_INSTRUCTIONS` and `MCP_SERVERS` (comma-separated `name=url`) replace `MCP_URL` and the hardcoded calculator prompt; console scripts are now `agent` and `agent-a2a`.
- `McpClient` now takes `{name: target}` and prefixes tool names (`calculator_add`) so several MCP servers can be used together.
- The Agent Card now has one skill per configured MCP server. Removed the `--demo` parser (`agents/offline.py`) and the structured-JSON A2A path; added `--tools` and `--call TOOL --args JSON` (no LLM needed).
- Added [docs/handbook.md](docs/handbook.md), the full agent reference, and this file.
- Redis key prefix is now `agent:memory:`. Tests: 33 → 21 (10 moved to `services`; calculator-specific ones removed).

## 0.1.0: 2026-10-08

First release (commits `fd48a63`, `8a157c0`). This is a historical record: since then the API and MCP server moved to `services/`, the package `calculator` became `agent`, and `--demo` was removed.

### Component versions

| Component | Version / identifier | Where it comes from |
|---|---|---|
| Agent package (`agents/calculator`) | 0.1.0 | `calculator/__init__.py`, `pyproject.toml` |
| REST API (Calculator API, OpenAPI) | 0.1.0 | `FastAPI(version=__version__)` |
| MCP server ("Calculator") | 0.1.0 (package version; the server sets none of its own) | FastMCP, Streamable HTTP at `/mcp` |
| A2A Agent Card | 0.1.0 | `build_agent_card()` |
| A2A protocol | 1.0, JSONRPC binding | `AgentInterface` in `card.py` |
| Python | ≥ 3.11 (tested on 3.12.5) | `requires-python` |

### Dependencies

Declared in `pyproject.toml`; "tested" is what the `.venv` resolved when this release was recorded.

| Package | Declared | Tested |
|---|---|---|
| fastapi | ≥ 0.115 | 0.142.4 |
| uvicorn[standard] | ≥ 0.30 | 0.54.0 |
| starlette (via fastapi) | n/a | 1.7.0 |
| httpx | ≥ 0.27 | 0.28.1 |
| fastmcp | **== 4.0.10** (pinned) | 4.0.10 |
| mcp (via fastmcp) | n/a | 2.3.0 |
| a2a-sdk[http-server] | ≥ 1.1.5, < 2 | 1.2.2 |
| openai | ≥ 1.99 | 3.26.1 |
| pydantic / pydantic-settings | n/a / ≥ 2.6 | 2.13.5 / 2.15.0 |
| redis (client) | ≥ 5.0 | 8.1.0 |

Dev extras: pytest ≥ 8 (9.1.1), pytest-asyncio ≥ 0.24 (1.4.0), fakeredis ≥ 2.26 (2.39.0), ruff ≥ 0.6 (0.16.10).

### Infrastructure (optional, `docker-compose.yml`)

| Service | Image | Port | Notes |
|---|---|---|---|
| Redis | `redis:7-alpine` | 6379 | conversation memory; enabled by `REDIS_URL` |
| LiteLLM proxy | `ghcr.io/berriai/litellm:main-stable` | 4000 | profile `litellm`; **floating tag, not pinned**, so the actual LiteLLM version can change between pulls. Pin a version tag or digest for reproducible runs |

LiteLLM models (`deploy/litellm/config.yaml`): `local-llm` → `ollama_chat/llama3.1` (Ollama on the host), `nvidia-llama` → `nvidia_nim/meta/llama-3.3-70b-instruct`.

### LLM provider defaults

| Provider | Base URL | Default model |
|---|---|---|
| nvidia (default) | `https://integrate.api.nvidia.com/v1` | `meta/llama-3.3-70b-instruct` |
| ollama | `http://localhost:11434/v1` | `llama3.1` |
| litellm | `http://localhost:4000/v1` | `local-llm` |
| openai | `https://api.openai.com/v1` | `gpt-4o-mini` |

Model catalogs change; the defaults are not guaranteed to exist later. Override with `LLM_MODEL`.

### Runtime defaults

| Item | Value |
|---|---|
| Ports | API 8000, MCP 8001, A2A 8002 (all bound to 127.0.0.1) |
| Agent loop limit | `MAX_STEPS = 5` |
| Memory | last 20 messages per session; Redis TTL 3600 s; key prefix `calculator:memory:` |
| Dev secrets | `CALCULATOR_API_KEY=dev-api-key`, `A2A_BEARER_TOKEN=dev-a2a-token` (localhost only) |
| A2A task store | in-memory (tasks lost on restart) |

### Capabilities

- REST API: `POST /add|subtract|multiply|divide`, `GET /health`; `X-API-Key` auth; NaN/Infinity rejected; divide by zero → 400.
- MCP: 4 tools, resource `calculator://help`, prompt `explain_calculation`.
- Agent: OpenAI-compatible tool-calling loop with conversation memory (in-process or Redis).
- A2A: Agent Card with skills `structured-arithmetic` and `natural-language-math`; bearer auth; Task lifecycle WORKING → COMPLETED/FAILED; no streaming; no cancellation.
- CLI `calculator-agent` with `--demo`, `--a2a`, `--session`.

### Changes

- Restructured into a self-contained project; built the full stack: FastAPI → MCP → LLM agent → A2A, with API-key and bearer auth.
- Added memory backends (in-process, Redis) and LLM presets (NVIDIA, Ollama, LiteLLM, OpenAI).
- Extracted shared code into `common/`; renamed package `calculator_agent` to `calculator`; split settings into `Settings` and `CalculatorSettings`; replaced `McpCalculator` with `McpClient(target)` and `require_api_key` with `api_key_auth(key_getter)`.
- Added the offline `--demo` mode, Makefile, Docker Compose (Redis, LiteLLM) and 33 offline tests.

### Verification

- 33 offline tests, as recorded in the project docs. Not re-run when this entry was written. Re-run `make test` and `make lint` before tagging a release.
- Not covered by automated tests: the real LLM path, live Redis, and the running network services.

### Known limitations

- The MCP endpoint has no authentication.
- The A2A bearer token is one shared static secret.
- The LiteLLM image tag is floating.

---

## Template for the next release

```markdown
## X.Y.Z: YYYY-MM-DD

### Component versions
(agent, API, MCP, Agent Card, A2A protocol, Python)

### Dependencies
(declared vs. tested; note changed pins)

### Infrastructure
(Redis and LiteLLM images, ports, LiteLLM models)

### LLM provider defaults
(only if changed)

### Changes
(added / changed / removed / fixed)

### Verification
(make test / make lint results, manual checks)

### Known limitations
```
