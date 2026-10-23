# AI Agent Playground

Monorepo of independent learning projects: `services/` (tools) and `agents/` (agents that use them). See [README.md](README.md); add agents per [docs/new-agent.md](docs/new-agent.md).

@AGENTS.md

## Projects

- `services/` — ready. Not an agent project: a home for FastAPI services, each with an MCP server (calculator first). Has its own [CLAUDE.md](services/CLAUDE.md). Agent projects reach it only via MCP URLs. Run everything from inside that folder (`.venv` lives there).
- `agents/<name>/` — one folder per agent, each a standalone project with a README that starts with its basis (API, RAG, ...). Index: [agents/README.md](agents/README.md).
  - `agents/calculator/` — ready, basis API. Has its own [CLAUDE.md](agents/calculator/CLAUDE.md) with commands, module map and gotchas. Run everything from inside that folder (`.venv` lives there).

## Release log

[RELEASE.md](RELEASE.md) lists changes per major commit; add an entry with each one.

## Shared tooling

- `.claude/rules/` — repo-structure, python, security rules.
- `.claude/skills/` — repo skills (`new-agent`, `new-service`, `release-entry`, `verify`) plus Anthropic's public `mcp-builder`, `skill-creator`, `webapp-testing` (from github.com/anthropics/skills, unmodified).
- `.claude/agents/layer-reviewer.md` — read-only reviewer subagent.
- `.claude/settings.json` — allowed commands; denies reading real `.env` files (not `.env.example`).
