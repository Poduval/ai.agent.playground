# AI Agent Playground

Monorepo of independent learning projects. See [README.md](README.md); add projects per [docs/new-project.md](docs/new-project.md).

@AGENTS.md

## Projects

- `building-agent-with-api/` — ready. Has its own [CLAUDE.md](building-agent-with-api/CLAUDE.md) with commands, module map and gotchas. Run everything from inside that folder (`.venv` lives there).
- `building-agent-with-rag/` — README-only placeholder.

## Shared tooling

- `.claude/rules/` — repo-structure, python, security rules.
- `.claude/agents/layer-reviewer.md` — read-only reviewer subagent.
- `.claude/settings.json` — allowed commands; denies reading real `.env` files (not `.env.example`).
