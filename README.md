# AI Agent Playground

A playground for learning and teaching how to build AI agents. [services](services/) holds the tools (FastAPI APIs with MCP servers); [agents](agents/) holds the agents that use them. Each is a complete, runnable project with its own dependencies, tests and docs.

| Project | Topics | Status |
|---|---|---|
| [services](services/) | FastAPI services, each with an MCP server for agents (calculator first); API-key auth | Ready |
| [agents/calculator](agents/calculator/) | Basis: API. MCP tools → LLM tool-calling agent → A2A (agent card, skills), Redis memory, bearer auth, NVIDIA / Ollama / LiteLLM | Ready |

Start with the `services` README, then [agents/calculator](agents/calculator/). To add an agent, see [docs/new-agent.md](docs/new-agent.md); to add tools, use the `new-service` skill. Pattern: build a service (API + MCP) → build an agent on it → add more of either.

## Principles

- Small and focused; readable top to bottom
- One project per folder, independently runnable (`cd <project> && make install && make test`)
- Provider-agnostic LLM access via OpenAI-compatible APIs
- Secrets only in `.env` (gitignored); each project ships `.env.example`

License: [MIT](LICENSE).
