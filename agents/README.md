# Agents

Each folder is a complete, independent agent project (own `pyproject.toml`, venv, tests, docs). The **basis** column says what the agent's abilities are grounded in. Agents reach the tools they use through MCP servers; the API-based ones use the servers built in [services](../services/).

| Agent | Basis | Topics | Status |
|---|---|---|---|
| [calculator](calculator/) | API | MCP client → LLM tool-calling loop → A2A, Redis memory, bearer auth, NVIDIA / Ollama / LiteLLM | Ready |

Start with [calculator](calculator/README.md). To add one, see [docs/new-agent.md](../docs/new-agent.md) (or the `new-agent` skill). Each agent's README starts with its **Basis** section. Agents never import from each other or from `services/`; shared helpers (`common/`) are copied into each agent to keep it self-contained.
