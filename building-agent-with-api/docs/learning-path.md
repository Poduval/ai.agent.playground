# Learning path

Read the code in this order; each step builds on the last and is under ~100 lines.

1. **REST** — `api/operations.py` → `api/main.py`. Run `make api`, open `/docs`, call `/add` with and without the API key.
2. **MCP** — `mcp_server/server.py`. Run `make mcp`; note tools vs resource vs prompt. Try `fastmcp` inspector or `agents/mcp_client.py`.
3. **LLM** — `llm/client.py`. Switch `LLM_PROVIDER` between nvidia and ollama; nothing else changes.
4. **Agent loop** — `agents/calculator_agent.py`. Watch the model request a tool, the result return, and the final answer.
5. **Memory** — `memory/store.py`. Ask "6 times 7", then "now add 8 to that" with the same `--session`. Set `REDIS_URL` and inspect keys `calculator_agent:memory:*` with `redis-cli`.
6. **A2A** — `a2a/card.py` (fetch `/.well-known/agent-card.json`), `a2a/executor.py`, `a2a/client.py`. Try a call without the bearer token.
7. **Security** — `security/auth.py` and the table in `architecture.md`.
8. **Tests** — `tests/` shows how to test every layer in-process without network or an LLM (fake LLM, ASGI transports, fakeredis).

Exercises: add a `power` operation end to end; add a second A2A skill; add rate limiting to the API; protect the MCP endpoint with auth.
