---
description: Where things go
---
- Top level: `services/` (FastAPI services, each with an MCP server), `agents/` (one folder per agent, `agents/<name>/`), plus root README/CLAUDE/AGENTS, `docs/` (cross-project only) and `.claude/`.
- Inside a project (`services/` or `agents/<name>/`): flat package dir, `tests/`, `docs/`, own `pyproject.toml`, `Makefile`, `.env.example`. No `src/`.
- Projects never import each other; agents reach `services/` only through MCP URLs. New config → settings class + `.env.example` + README. New dependency → that project's `pyproject.toml`.
- Add new agents to `agents/README.md` and the root README table; each agent README starts with its basis (API, RAG, ...).
