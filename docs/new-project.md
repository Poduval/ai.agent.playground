# Adding a project

Each top-level `building-agent-with-*` folder is a complete, independent project.

```text
building-agent-with-<topic>/
├── README.md          what it teaches, quick start, providers, security notes
├── CLAUDE.md          commands + module map for AI assistants
├── pyproject.toml     its own dependencies and console scripts
├── Makefile           install / test / lint / run targets
├── .env.example       every env var, placeholders only
├── <package>/         flat layout, one subpackage per concept
├── tests/             offline tests (fakes, no network or API keys)
└── docs/              architecture + learning path
```

Rules: no imports between projects; copy small helpers instead of sharing; keep code short and teachable; add the project to the root README table.
