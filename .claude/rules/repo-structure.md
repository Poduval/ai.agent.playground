---
description: Where things go
---
- Top level: one folder per project (`building-agent-with-<topic>`), plus root README/CLAUDE/AGENTS, `docs/` (cross-project only) and `.claude/`.
- Inside a project: flat package dir, `tests/`, `docs/`, own `pyproject.toml`, `Makefile`, `.env.example`. No `src/`.
- Projects never import each other. New config → settings class + `.env.example` + README. New dependency → that project's `pyproject.toml`.
- Add new projects to the root README table.
