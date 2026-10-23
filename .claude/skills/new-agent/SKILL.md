---
name: new-agent
description: Add a new agent project (e.g. agents/docs-qa) to the playground by copying agents/calculator. Use when asked to add an agent, whether API-based, RAG-based or other. For an API or MCP server use new-service.
---
Follow docs/new-agent.md and .claude/rules/repo-structure.md. Read agents/calculator/CLAUDE.md first.

1. Copy `agents/calculator/` to `agents/<name>/` (without `.venv`, caches, RELEASE.md); rename the project in `pyproject.toml` and console scripts if they would clash.
2. README.md: start with a **Basis** section (API, RAG, ...: what the agent's abilities are grounded in and what it teaches). Update CLAUDE.md and docs.
3. Behaviour via settings first: `AGENT_NAME`, `AGENT_INSTRUCTIONS`, `MCP_SERVERS` (comma-separated `name=url`, servers built with `new-service`). Write new code only if the basis needs it (e.g. a retrieval layer); config only via settings, every env var in `.env.example` and README.
4. Never import from other agents or from `services/`. Never add a top-level `a2a.py` or relative imports (they would shadow the SDK). Give the agent its own ports and Redis prefix if run alongside others.
5. Tests: offline only, with `FakeLLM` and a stand-in MCP server from `tests/fakes.py`.
6. Add the agent to `agents/README.md`, the root README table and the root CLAUDE.md; add a RELEASE.md entry (`release-entry`); run `verify`.
