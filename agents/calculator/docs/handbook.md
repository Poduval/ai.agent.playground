# Agent Handbook

The complete reference for the agent built in `agents/calculator`: what it is, how each layer works, and a guided tour of the code. For a short overview see the [README](../README.md); for reading order see [learning-path.md](learning-path.md); for the security table and extension points see [architecture.md](architecture.md).

## Contents

1. [What the agent is](#1-what-the-agent-is)
2. [Architecture at a glance](#2-architecture-at-a-glance)
3. [Running it](#3-running-it)
4. [Configuration reference](#4-configuration-reference)
5. [Codebase walkthrough](#5-codebase-walkthrough)
6. [End-to-end flows](#6-end-to-end-flows)
7. [Security](#7-security)
8. [Testing](#8-testing)
9. [Extending the agent](#9-extending-the-agent)
10. [Troubleshooting](#10-troubleshooting)
11. [Glossary](#11-glossary)

---

## 1. What the agent is

The **Agent** is a generic tool-using assistant: it discovers the tools of whatever MCP servers you configure (`MCP_SERVERS`) and lets an LLM use them. The servers in `../../services` (the calculator first) provide the tools; the arithmetic is trivial on purpose, because the project exists to show every layer you need to build a real agent, each in one short file.

| Layer | Role | Technology |
|---|---|---|
| REST API (in `services`) | The "business system": does the actual work, enforces auth and validation | FastAPI |
| MCP server (in `services`) | Exposes the API to models as tools, a resource and a prompt | FastMCP |
| LLM client | One client for many providers | OpenAI SDK (`AsyncOpenAI`) |
| Agent | Loop in which the model picks tools; keeps conversation memory | plain Python |
| Memory | Per-session chat history | in-process or Redis |
| A2A | Makes the agent a discoverable, authenticated service for other agents | `a2a-sdk` + Starlette |

The model never does arithmetic itself. The instructions (`AGENT_INSTRUCTIONS`) tell it to use the tools, and every number comes from the REST API.

Ways to use the agent:

| Mode | Command | Needs LLM? | Path |
|---|---|---|---|
| Inspect | `--tools` | No | MCP `list_tools` |
| Direct tool call | `--call TOOL --args JSON` | No | MCP → API |
| Ask | *(default)* | Yes | LLM agent → MCP → API |
| A2A | `--a2a` | Yes | A2A server → executor → agent → MCP → API |

## 2. Architecture at a glance

```text
 CLI / other agents
        │  A2A  (Agent Card, skills, bearer auth, tasks)        :8002
        ▼
 Agent ──► LLM (NVIDIA / Ollama / LiteLLM / OpenAI) + memory (Redis)
        │  MCP  (tools, resource, prompt)                        :8001/mcp
        ▼
 MCP Server ──HTTP + X-API-Key──►  FastAPI Calculator     (../../services: :8001, :8000)
```

Code is split in two packages:

- **`common/`** is reusable by any agent and knows nothing about calculators: settings, LLM client, memory stores, auth, MCP client.
- **`agent/`** is the agent: agent loop, A2A wrapper, CLI. The API and MCP server it calls live in the root [services](../../../services/) project.

Dependencies point one way: `agent` imports `common`, never the reverse. To tune this agent, change `AGENT_INSTRUCTIONS` and `MCP_SERVERS` (see [section 9](#9-extending-the-agent)); a different kind of agent gets its own folder under `agents/`.

Ports: A2A 8002 (API 8000 and MCP 8001 are in `services`) · Redis 6379 · LiteLLM 4000 · Ollama 11434. All servers bind to `127.0.0.1`.

## 3. Running it

Requirements: Python ≥ 3.11; Docker only for optional Redis/LiteLLM.

```bash
cd agents/calculator
make install                 # .venv + editable install with dev tools
cp .env.example .env         # set NVIDIA_API_KEY, or LLM_PROVIDER=ollama
```

Start the calculator service from `../../services` (`make calculator-api`, `make calculator-mcp`), then here:

```bash
make a2a     # :8002
```

Ask questions:

```bash
.venv/bin/agent --tools                                         # no LLM: list MCP tools
.venv/bin/agent --call calculator_divide --args '{"a": 84, "b": 2}'   # no LLM
.venv/bin/agent "What is 6 times 7?"                             # LLM + MCP
.venv/bin/agent --a2a "Multiply 6 by 7"                          # via A2A
.venv/bin/agent --session demo "Add 8 to that"                   # memory
```

Useful URLs: Agent Card <http://127.0.0.1:8002/.well-known/agent-card.json>.

Other make targets: `make test`, `make lint`, `make redis`, `make litellm`.

### Choosing an LLM provider

| `LLM_PROVIDER` | Default model | Key | Notes |
|---|---|---|---|
| `nvidia` (default) | `meta/llama-3.3-70b-instruct` | `NVIDIA_API_KEY` | free at build.nvidia.com |
| `ollama` | `llama3.1` | none | run `ollama pull llama3.1` first |
| `litellm` | `local-llm` | `LITELLM_API_KEY` (optional) | `make litellm`; models defined in `deploy/litellm/config.yaml` |
| `openai` | `gpt-4o-mini` | `OPENAI_API_KEY` | |

The model must support tool calling. Override with `LLM_MODEL`.

## 4. Configuration reference

All config goes through pydantic-settings: environment variables first, then `.env`. Names are case-insensitive. Template: [.env.example](../.env.example).

| Variable | Default | Defined in | Meaning |
|---|---|---|---|
| `LLM_PROVIDER` | `nvidia` | `common/config.py` | preset name |
| `LLM_MODEL` | *(preset)* | | overrides preset model |
| `LLM_BASE_URL` | *(preset)* | | overrides preset URL |
| `LLM_API_KEY` | | | overrides the provider-specific key |
| `NVIDIA_API_KEY` / `OPENAI_API_KEY` / `LITELLM_API_KEY` | | | provider keys |
| `A2A_BEARER_TOKEN` | `dev-a2a-token` | | token for the A2A endpoint |
| `REDIS_URL` | *(empty)* | | empty = in-process memory |
| `MEMORY_TTL_SECONDS` | `3600` | | Redis idle expiry |
| `MEMORY_MAX_MESSAGES` | `20` | | messages kept per session |
| `MCP_SERVERS` | `calculator=http://127.0.0.1:8001/mcp` | `agent/config.py` | comma-separated `name=url` MCP servers; the name prefixes tool names (`calculator_add`) |
| `AGENT_NAME` | `Assistant` | | name in the Agent Card |
| `AGENT_INSTRUCTIONS` | *(generic helper prompt)* | | system prompt and Agent Card description |
| `A2A_URL` | `http://127.0.0.1:8002` | | A2A address (also in the Agent Card) |

Settings are split: `common.config.Settings` holds what every agent needs; `agent.config.AgentSettings` extends it. The `.env` file is read from the current working directory, so run commands from `agents/calculator/`. The API key and API URL are settings of the calculator service (see `services/.env.example`).

## 5. Codebase walkthrough

```text
common/
  config.py            base Settings
  llm/client.py        provider presets → AsyncOpenAI
  memory/store.py      MemoryStore protocol, InMemoryStore, RedisStore
  security/auth.py     BearerTokenMiddleware
  mcp_client.py        McpClient
agent/
  config.py            AgentSettings
  main.py              Agent (tool loop + memory)
  a2a/                 card.py, executor.py, server.py, client.py
  cli.py               `agent` command
tests/                 offline suite
deploy/litellm/        LiteLLM proxy config
docker-compose.yml     Redis, LiteLLM
```

### 5.1 REST API and 5.2 MCP server: moved to `../../services/`

The calculator FastAPI app and its MCP server (`add`, `subtract`, `multiply`, `divide`, the `calculator://help` resource and the `explain_calculation` prompt) now live in the [services](../../../services/README.md) project, next to any other API you add. This agent only needs the server URLs (`MCP_SERVERS`, default `calculator=http://127.0.0.1:8001/mcp`); it never imports from `services`. Start them there with `make calculator-api` and `make calculator-mcp`.

### 5.3 LLM client: `common/llm/client.py`

NVIDIA, Ollama, LiteLLM and OpenAI all speak the OpenAI chat-completions API, so one `AsyncOpenAI` client covers them.

- `PRESETS` maps provider → `(base_url, default_model, key_field)`.
- `resolve_llm_config()` returns an `LLMConfig` after applying overrides. Errors: unknown provider → `ValueError`; missing key → `RuntimeError` naming the variable to set. Ollama needs no key, so a dummy value is used.
- `get_llm_client()` builds the client.

Adding a provider means adding one line to `PRESETS`.

### 5.4 MCP client: `common/mcp_client.py`

`McpClient(servers)` wraps the FastMCP client. `servers` maps a name to a URL, or to a FastMCP server object for in-memory tests.

- `openai_tools()` lists the tools of every server and converts each to OpenAI's `{"type": "function", "function": {name, description, parameters}}` format. Names get the server name as prefix (`calculator_add`), so two servers can never collide. This is why the agent never hardcodes tools.
- `call(name, arguments)` routes a prefixed name to its server, runs the tool and returns the result value. Tool errors become `RuntimeError`.
- Connection failures are rewritten as "Cannot reach the MCP server at … Is it running?", unwrapping the exception groups FastMCP may produce.

A new connection is opened per call. That is simple and fine for a template.

### 5.5 Agent loop: `agent/main.py`

`Agent(mcp, memory, llm, model)`: all dependencies are injectable, defaulting to the configured ones. Tests inject a fake LLM.

`run(question, session_id="default")`:

1. Fetch tools from MCP.
2. Build messages: system prompt (`AGENT_INSTRUCTIONS`) + stored history + the new user message.
3. Loop up to `MAX_STEPS = 5`:
   - Call the LLM with `tools`.
   - No tool calls → save the user question and assistant answer to memory, return the answer.
   - Tool calls → append the assistant message, run each call through MCP, append a `tool` message per call. On error the text `Error: …` is sent back so the model can explain or retry.
4. After 5 steps without an answer, raise `RuntimeError`.

Only the final user/assistant text is persisted, not intermediate tool messages, which keeps history small and always valid for the next request.

### 5.6 Memory: `common/memory/store.py`

The `MemoryStore` protocol has three async methods: `history(session_id)`, `append(session_id, role, content)`, `clear(session_id)`. Messages are `{"role", "content"}` dicts.

| Store | Storage | Behavior |
|---|---|---|
| `InMemoryStore` | dict of `deque(maxlen=N)` | lost on restart; per process |
| `RedisStore` | list at `agent:memory:<session>` | `RPUSH` + `LTRIM` to cap + `EXPIRE` for idle TTL; survives restarts and is shared across processes |

`get_store()` returns Redis when `REDIS_URL` is set. Memory is short-term conversation context only: no summarization, no semantic search. The Redis key prefix is `agent:memory:`, so a second agent sharing a Redis should use its own prefix.

### 5.7 A2A: `agent/a2a/`

Agent-to-Agent turns the agent into a network service other agents can discover and call.

- **[card.py](../agent/a2a/card.py)**: `build_agent_card()` produces the Agent Card served at `/.well-known/agent-card.json` (public). It declares the JSONRPC interface URL, input/output modes, a bearer security scheme and one skill per configured MCP server (so the card stays accurate as servers are added). Name and description come from `AGENT_NAME` / `AGENT_INSTRUCTIONS`.

- **[executor.py](../agent/a2a/executor.py)**: `ToolAgentExecutor.execute` emits the Task, then `WORKING`, then an `answer` artifact, then `COMPLETED` (or `FAILED` with the error text; exceptions are reported, not raised). `_solve` runs the `Agent`, using the task's `context_id` as the memory session. The agent is built lazily, so the card can be served without an LLM key. `cancel` is unsupported.
- **[server.py](../agent/a2a/server.py)**: `build_app()` assembles a Starlette app: card routes + JSON-RPC route at `/`, wrapped in `BearerTokenMiddleware`, with an `InMemoryTaskStore`.
- **[client.py](../agent/a2a/client.py)**: `ask_agent(text, context_id)` discovers the agent from its card, sends the message with the bearer token, and returns the latest non-empty text from the response stream.

### 5.8 Security helper: `common/security/auth.py`

- `BearerTokenMiddleware` is an ASGI middleware requiring `Authorization: Bearer <token>`, except for paths under `/.well-known/`. Failure → 401 with `WWW-Authenticate: Bearer`.
- It compares with `hmac.compare_digest` (constant time). The REST API's `api_key_auth` lives in `services/common/security/`.

### 5.9 CLI: `agent/cli.py`

`agent "question" [--a2a] [--session ID]`, or `agent --tools`, or `agent --call TOOL --args JSON`. The default session is `cli`. `--session` is the memory key for direct mode and the A2A `context_id` for `--a2a`. Errors print `Error: …` to stderr and exit with code 1.

## 6. End-to-end flows

### Direct (LLM) mode: "What is 6 times 7?"

```text
CLI → Agent.run
        ├─ McpClient.openai_tools()   → MCP list_tools
        ├─ MemoryStore.history(session)
        ├─ LLM  → tool_call calculator_multiply {a:6, b:7}
        ├─ McpClient.call("calculator_multiply") → MCP tool → POST /multiply (X-API-Key) → 42.0
        ├─ LLM  → "6 times 7 is 42."
        └─ MemoryStore.append(user, assistant)
```

### A2A mode

```text
CLI → ask_agent (Bearer) → A2A server → BearerTokenMiddleware
    → DefaultRequestHandler → ToolAgentExecutor.execute
        Task → WORKING → Agent.run → artifact → COMPLETED/FAILED
    ← stream of events; client returns the latest text
```

### Memory follow-up

Run `agent --session demo "What is 6 times 7?"`, then `agent --session demo "Now add 8 to that"`. The second call loads the first turn from memory, so the model can resolve "that". With in-process memory this only works within one long-lived process (such as the A2A server, which keeps the agent for its lifetime). Separate CLI runs need `REDIS_URL`, because each one starts a new process.

## 7. Security

| Boundary | Protection |
|---|---|
| Client → REST API | `X-API-Key`, constant-time compare; `/health` public |
| MCP server → REST API | forwards the configured API key |
| Client → A2A | bearer token; Agent Card public |
| Inputs | Pydantic validation; NaN/Infinity rejected; divide-by-zero → 400 |
| LLM output | tool names and arguments are untrusted; they are executed only via MCP tools whose schemas, and then the REST API, validate them |
| MCP endpoint | **not authenticated** in this template (localhost only). Add FastMCP auth before exposing it |
| Secrets | env or gitignored `.env` only |

Operational rules: change `dev-api-key` and `dev-a2a-token` anywhere beyond localhost; keep servers bound to `127.0.0.1`; never commit `.env`. The A2A token is a single shared static secret with no per-caller identity, rotation or rate limiting.

## 8. Testing

```bash
make test    # 21 tests, offline: no network, servers, LLM or Redis
make lint    # ruff
```

| File | Covers |
|---|---|
| `test_agent_loop.py` | settings parsing, MCP client (prefixing, several servers, errors), agent loop with a fake LLM, instructions from settings |
| `fakes.py` | stand-in calculator MCP server and scripted `FakeLLM` (the real MCP server is in `services`) |
| `test_agent_a2a.py` | Agent Card, public card vs. authenticated RPC, text round trip, tool errors relayed |
| `test_common_memory.py` | history round trip, session isolation, cap, clear (both stores; Redis via fakeredis) |
| `test_common_security_and_llm.py` | bearer middleware, provider presets, missing key, unknown provider |

How tests stay offline: ASGI transports call the Starlette apps in-process; `tests/fakes.py` replaces the real MCP server; `McpClient` accepts a server object; `FakeLLM` scripts tool calls; `conftest.py` pins settings through env vars so a local `.env` cannot change results.

**Not covered:** the real LLM path (NVIDIA/Ollama/OpenAI), a live Redis server and real network services. Verify those manually.

## 9. Extending the agent

| Goal | What to do |
|---|---|
| New tool or operation (e.g. `power`) | add it in `services/calculator` (`api/operations.py` and an `@mcp.tool`). The agent discovers it automatically. |
| New service the agent should use | build it in `../../services` (`new-service` skill), then add `name=url` to `MCP_SERVERS` |
| New LLM provider | add a `PRESETS` entry in `common/llm/client.py` (and a key field in `common/config.py` if needed) |
| New memory backend | implement `MemoryStore` in `common/memory/` and select it in `get_store()` |
| Persistent A2A tasks | replace `InMemoryTaskStore` in `a2a/server.py` |
| Protect MCP | add FastMCP auth and send credentials from `McpClient` |
| Change this agent's behaviour | set `AGENT_NAME`, `AGENT_INSTRUCTIONS` and `MCP_SERVERS` in `.env` |
| A different agent (e.g. RAG-based) | add a folder under `agents/` by copying this one (see [docs/new-agent.md](../../../docs/new-agent.md)); agents never share code, so `common/` is copied |

Conventions from the repo rules: keep code short and commented where a learner would ask "why"; configuration only through the settings class, with new variables documented in `.env.example` and the README; new dependencies go in this project's `pyproject.toml`; tests must run offline; log changes in the root `RELEASE.md`.

## 10. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `Cannot reach the MCP server at … Is it running?` | start `make calculator-mcp` and `make calculator-api` in `../../services` |
| `No API key for provider 'nvidia'. Set NVIDIA_API_KEY` | set it in `.env`, or use `LLM_PROVIDER=ollama`, `--tools` or `--call` |
| `Unknown LLM_PROVIDER` | use `nvidia`, `ollama`, `litellm` or `openai` |
| API returns 401 | `X-API-Key` must equal `CALCULATOR_API_KEY` in `services/.env`; the MCP server and API share that value |
| A2A returns 401 | send `Authorization: Bearer <A2A_BEARER_TOKEN>` |
| `No final answer after 5 steps` | model keeps calling tools; try a stronger model with tool-calling support |
| Model ignores tools or errors on `tools` | the chosen model lacks tool-calling support; override `LLM_MODEL` |
| Follow-up questions forget context | in-process memory is per process; set `REDIS_URL` and reuse `--session` |
| `.env` values not picked up | run from `agents/calculator/`; real environment variables override `.env` |
| Weird import errors about `a2a` | never add a top-level `a2a.py` or relative imports; `agent.a2a` shares its name with the SDK (absolute imports keep them apart) |
| SDK API mismatch after upgrade | `fastmcp` is pinned and `a2a-sdk` bounded `<2`; check the source in `.venv` |

## 11. Glossary

- **Agent**: a program where an LLM decides which actions (tools) to take, in a loop, until it can answer.
- **Tool calling**: the LLM returns a structured request (name + JSON arguments) instead of text; your code executes it and returns the result.
- **MCP (Model Context Protocol)**: open standard for exposing tools, resources and prompts to LLM applications.
- **A2A (Agent2Agent)**: open protocol for agents to discover and call each other over HTTP.
- **Agent Card**: public JSON document describing an A2A agent: skills, interfaces, security.
- **Skill**: a capability advertised on the Agent Card.
- **Task / context**: A2A work unit and the conversation it belongs to; `context_id` doubles as the memory session id here.
- **Artifact**: an output of a Task (here, the `answer` text).
- **Session**: a conversation identifier used as the memory key.
