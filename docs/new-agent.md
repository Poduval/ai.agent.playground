# Adding an agent

Every folder in `agents/` is a complete, independent agent project. The folder name is the agent (`agents/calculator`, `agents/docs-qa`, ...).

```text
agents/<name>/
├── README.md          basis of the agent (API, RAG, ...), what it teaches, quick start
├── CLAUDE.md          commands + module map for AI assistants
├── pyproject.toml     its own dependencies and console scripts
├── Makefile           install / test / lint / run targets
├── .env.example       every env var, placeholders only
├── agent/             flat layout, one subpackage per concept (a2a/, ...)
├── common/            LLM, memory, security, MCP client (copied, not shared)
├── tests/             offline tests (fakes, no network or API keys)
└── docs/              architecture + learning path
```

Easiest start: copy `agents/calculator/`, then change the README "Basis" section, settings (`AGENT_*`, `MCP_SERVERS`) and whatever code the new basis needs.

**Basis.** Say what the agent's abilities are grounded in, at the top of its README:
- **API**: tools from REST APIs exposed by MCP servers in `services/` (see `agents/calculator`).
- **RAG**: retrieval over documents (chunking, embeddings, vector store), ideally exposed as an MCP tool.
- or anything else; one sentence on what it teaches.

Rules: no imports between agents or from `services/` (reach services through MCP URLs); copy small helpers instead of sharing; keep code short and teachable; register the agent in `agents/README.md` and the root README table. Tools for agents are built in `services/` (see the `new-service` skill).
