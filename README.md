# AI Agent Playground

A collection of small, self-contained projects for learning and teaching how to build AI agents. Each project is a complete, runnable template with its own dependencies, tests and docs.

| Project | Topics | Status |
|---|---|---|
| [building-agent-with-api](building-agent-with-api/) | FastAPI → MCP → LLM tool-calling agent → A2A (agent card, skills), Redis memory, API-key and bearer auth, NVIDIA / Ollama / LiteLLM | Ready |
| [building-agent-with-rag](building-agent-with-rag/) | Retrieval-augmented generation | Placeholder |

Start with the first project's README. To add another, see [docs/new-project.md](docs/new-project.md).

## Principles

- Small and focused; readable top to bottom
- One project per folder, independently runnable (`cd <project> && make install && make test`)
- Provider-agnostic LLM access via OpenAI-compatible APIs
- Secrets only in `.env` (gitignored); each project ships `.env.example`

License: [MIT](LICENSE).
