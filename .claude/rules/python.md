---
description: Python style for this repo
paths:
  - "**/*.py"
---
- Type hints on signatures, short docstrings, `async` for I/O; line length 140 (ruff).
- Read config via `get_settings()`; never `os.getenv` scattered in modules.
- LLM access only through the project's `llm` package; keep it OpenAI-compatible.
- Tests: offline only (fake LLM, `httpx.ASGITransport`, fakeredis). Run the project's `make test` and `make lint`.
