# Release Log

Changes only, newest first. Add an entry with each major commit (commit hash, date, what changed).

## 8a157c0 — 2026-10-08
- Added `building-agent-with-api/common/` with the shared config, LLM, memory, security and MCP client code.
- Renamed package `calculator_agent` to `calculator`; `agents/calculator_agent.py` is now `agents/main.py`; `mcp_server/` is now `mcp/`.
- Split settings: base `Settings` in `common`, `CalculatorSettings` in `calculator`.
- Replaced `McpCalculator` with the generic `McpClient(target)` and `require_api_key` with the `api_key_auth(key_getter)` factory.
- Renamed Redis key prefix to `calculator:memory:`.
- Split tests into `test_common_*` and `test_calculator_*`.
- Updated CLAUDE.md, README and docs; added an "adding an agent" recipe.

## fd48a63 — 2026-10-08
- Restructured the repo into self-contained projects: `building-agent-with-api/` and a `building-agent-with-rag/` placeholder.
- Removed the concept placeholder folders (`agents`, `evaluation`, `llm`, `mcp`, `memory`, `microsoft-agent-framework`, `multi-agent`, `rag`, `shared`, `tool-calling`, `workflows`).
- Added the calculator stack: FastAPI (add, subtract, multiply, divide) → MCP server → LLM tool-calling agent → A2A agent.
- Added the Agent Card with two skills and a bearer security scheme.
- Added API-key auth for the REST API and bearer-token auth for A2A.
- Added conversation memory with in-process and Redis backends.
- Added LLM provider presets: NVIDIA, Ollama, LiteLLM, OpenAI.
- Added an offline `--demo` mode, a CLI, a Makefile, optional Docker Compose (Redis, LiteLLM) and 33 offline tests.
- Added CLAUDE.md, AGENTS.md, `.claude/` rules, a reviewer subagent and settings, and `docs/new-project.md`.

## 6b12b49 — 2026-08-12
- Established the concept-first folder structure with a README per concept.

## 19e3279 — 2026-08-12
- Initial commit.
