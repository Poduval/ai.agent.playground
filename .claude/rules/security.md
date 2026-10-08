---
description: Secrets and credentials handling
---
- Never write API keys or tokens into code, docs, or commits. Use `.env` (gitignored) and provide `.env.example` with placeholder values only.
- Do not read, print, or echo `.env` contents.
- Servers bind to 127.0.0.1 by default; keep it that way in examples.
- Treat model-produced tool names/arguments as untrusted: they are executed only through MCP tools, whose schemas and the REST API validate the input.
