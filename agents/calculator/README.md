# Calculator Agent

Part of the [AI Agent Playground](../../README.md) · one of the [agents](../README.md).

## Basis: API

This agent gets its abilities from a **REST API exposed over MCP**. It has no knowledge base and no retrieval: everything it can do comes from the tools of the MCP servers in [services](../../services/), here the calculator service (`add`, `subtract`, `multiply`, `divide`). Use this agent to learn the API → MCP → LLM → A2A path; for retrieval-based agents see the other folders in [agents](../README.md).

| | |
|---|---|
| Grounded in | REST API tools via MCP (`MCP_SERVERS`) |
| Needs | the [calculator service](../../services/calculator/) running |
| Teaches | MCP client, tool-calling loop, conversation memory, A2A, auth |

A small, readable template for learning (and teaching) how to build agents in layers — each layer is one short file you can read in a few minutes.

```text
 CLI / other agents
        │  A2A  (Agent Card, skills, bearer auth, tasks)
        ▼
 Agent ──► LLM (NVIDIA / Ollama / LiteLLM / OpenAI) + memory (Redis)
        │  MCP  (tools, resource, prompt)
        ▼
 MCP Server ──HTTP + X-API-Key──►  FastAPI Calculator   (both in ../../services)
```

| Layer | Concept | Where |
|---|---|---|
| REST API | Plain service, validation, API-key auth | [services/calculator/api/](../../services/calculator/api/) |
| MCP | Expose the API as tools / resource / prompt | [services/calculator/mcp/](../../services/calculator/mcp/) |
| LLM | One OpenAI-compatible client, many providers | [common/llm/](common/llm/) |
| Agent | Tool-calling loop over MCP tools, with memory | [agent/main.py](agent/main.py) |
| Memory | In-process or Redis conversation history | [common/memory/](common/memory/) |
| A2A | Agent Card, skills, executor, client, bearer auth | [agent/a2a/](agent/a2a/) |
| Security | Bearer middleware here; API key and input validation in `services` | [common/security/](common/security/) |

The full reference is the [handbook](docs/handbook.md). Read [docs/architecture.md](docs/architecture.md) for the request flow and [docs/learning-path.md](docs/learning-path.md) for a suggested reading order.

## Quick start

```bash
# 1. the calculator service (REST API + MCP server)
cd services                  # from the repo root
make install
make calculator-api          # terminal 1
make calculator-mcp          # terminal 2

# 2. this agent
cd ../agents/calculator
make install                 # creates .venv, installs the package + dev tools
cp .env.example .env         # add NVIDIA_API_KEY (free at build.nvidia.com) or choose ollama
make a2a                     # terminal 3 (only for --a2a)
```

Then:

```bash
.venv/bin/agent --tools                                          # no LLM needed: list the MCP tools
.venv/bin/agent --call calculator_divide --args '{"a": 84, "b": 2}'   # no LLM needed
.venv/bin/agent "What is 6 times 7?"                             # LLM picks the MCP tool
.venv/bin/agent --a2a "Multiply 6 by 7"                          # via the A2A agent
.venv/bin/agent --session demo "Now add 8 to that"               # memory: follow-up questions
```

The agent itself is generic: list more servers from `services` in `MCP_SERVERS` (comma-separated `name=url`) and it uses all their tools.

Interactive API docs: http://127.0.0.1:8000/docs (send header `X-API-Key: dev-api-key`), served by the service.

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
make test    # 21 tests, no network, no servers, no LLM key needed
make lint
```

## Security notes

- The default keys in `.env.example` are for localhost only; change them anywhere else.
- Servers bind to `127.0.0.1`. The MCP endpoint (in `services`) is unauthenticated in this template (see [docs/architecture.md](docs/architecture.md#security-model)).

## Project layout

```text
common/             shared building blocks: config, llm, memory, security, MCP client
agent/              the agent: tool loop, a2a, cli
tests/              pytest suite
docs/               architecture and learning path
deploy/             optional infrastructure config (LiteLLM)
docker-compose.yml  optional Redis / LiteLLM
```

License: see the repository [LICENSE](../../LICENSE).
