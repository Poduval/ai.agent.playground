# Learning path

Read the code in this order; each step builds on the last and is under ~100 lines.

1. **REST** — `calculator/api/operations.py` → `calculator/api/main.py`. Run `make api`, open `/docs`, call `/add` with and without the API key.
2. **MCP** — `calculator/mcp/server.py`. Run `make mcp`; note tools vs resource vs prompt. Try `fastmcp` inspector or `common/mcp_client.py`.
3. **LLM** — `common/llm/client.py`. Switch `LLM_PROVIDER` between nvidia and ollama; nothing else changes.
4. **Agent loop** — `agents/main.py`. Watch the model request a tool, the result return, and the final answer.
5. **Memory** — `common/memory/store.py`. Ask "6 times 7", then "now add 8 to that" with the same `--session`. Set `REDIS_URL` and inspect keys `calculator:memory:*` with `redis-cli`.
6. **A2A** — `calculator/a2a/card.py` (fetch `/.well-known/agent-card.json`), `calculator/a2a/executor.py`, `calculator/a2a/client.py`. Try a call without the bearer token.
7. **Security** — `common/security/auth.py` and the table in `architecture.md`.
8. **Tests** — `tests/` shows how to test every layer in-process without network or an LLM (fake LLM, ASGI transports, fakeredis).

Exercises: add a `power` operation end to end; add a second A2A skill; add rate limiting to the API; protect the MCP endpoint with auth.
