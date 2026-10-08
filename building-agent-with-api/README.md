# Building an Agent with an API

Part of the [AI Agent Playground](../README.md). A small, readable template for learning (and teaching) how to build agents in layers — each layer is one short file you can read in a few minutes.

```text
 CLI / other agents
        │  A2A  (Agent Card, skills, bearer auth, tasks)
        ▼
 Calculator Agent ──► LLM (NVIDIA / Ollama / LiteLLM / OpenAI) + memory (Redis)
        │  MCP  (tools, resource, prompt)
        ▼
 MCP Server ──HTTP + X-API-Key──►  FastAPI Calculator (add, subtract, multiply, divide)
```

| Layer | Concept | Where |
|---|---|---|
| REST API | Plain service, validation, API-key auth | [calculator_agent/api/](calculator_agent/api/) |
| MCP | Expose the API as tools / resource / prompt | [calculator_agent/mcp_server/](calculator_agent/mcp_server/) |
| LLM | One OpenAI-compatible client, many providers | [calculator_agent/llm/](calculator_agent/llm/) |
| Agent | Tool-calling loop over MCP tools, with memory | [calculator_agent/agents/](calculator_agent/agents/) |
| Memory | In-process or Redis conversation history | [calculator_agent/memory/](calculator_agent/memory/) |
| A2A | Agent Card, skills, executor, client, bearer auth | [calculator_agent/a2a/](calculator_agent/a2a/) |
| Security | API key, bearer middleware, input validation | [calculator_agent/security/](calculator_agent/security/) |

Read [docs/architecture.md](docs/architecture.md) for the request flow and [docs/learning-path.md](docs/learning-path.md) for a suggested reading order.

## Quick start

```bash
cd building-agent-with-api
make install                 # creates .venv, installs the package + dev tools
cp .env.example .env         # add NVIDIA_API_KEY (free at build.nvidia.com) or choose ollama
```

Run each in its own terminal: `make api`, `make mcp`, `make a2a`. Then:

```bash
.venv/bin/calculator-agent --demo "What is 84 divided by 2?"   # no LLM needed
.venv/bin/calculator-agent "What is 6 times 7?"                  # LLM picks the MCP tool
.venv/bin/calculator-agent --a2a "Multiply 6 by 7"               # via the A2A agent
.venv/bin/calculator-agent --session demo "Now add 8 to that"    # memory: follow-up questions
```

Interactive API docs: http://127.0.0.1:8000/docs (send header `X-API-Key: dev-api-key`).

## LLM providers

Set `LLM_PROVIDER` in `.env`:

| Provider | Setup |
|---|---|
| `nvidia` (default) | Free API key from [build.nvidia.com](https://build.nvidia.com) → `NVIDIA_API_KEY` |
| `ollama` | `ollama pull llama3.1` and keep Ollama running; no key needed |
| `litellm` | `make litellm` (config in [deploy/litellm/](deploy/litellm/config.yaml)) and `LLM_MODEL=local-llm` |
| `openai` | `OPENAI_API_KEY` |

Models change often — override with `LLM_MODEL`. The model must support tool calling.

## Memory with Redis

`make redis`, then set `REDIS_URL=redis://localhost:6379/0`. Without it, memory lives in the process.

## Tests and quality

```bash
make test    # 33 tests, no network, no servers, no LLM key needed
make lint
```

## Security notes

- The default keys in `.env.example` are for localhost only; change them anywhere else.
- Servers bind to `127.0.0.1`. The MCP endpoint itself is unauthenticated in this template (see [docs/architecture.md](docs/architecture.md#security-model)).

## Project layout

```text
calculator_agent/   application code (one subpackage per layer)
tests/              pytest suite
docs/               architecture and learning path
deploy/             optional infrastructure config (LiteLLM)
docker-compose.yml  optional Redis / LiteLLM
```

License: see the repository [LICENSE](../LICENSE).
