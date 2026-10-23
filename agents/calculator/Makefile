.PHONY: install test lint a2a redis litellm

install:        ## create .venv and install with dev tools
	python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
test:
	.venv/bin/pytest
lint:
	.venv/bin/ruff check common agent tests
a2a:            ## needs the MCP servers from ../../services
	.venv/bin/agent-a2a
redis:          ## optional memory backend
	docker compose up -d redis
litellm:        ## optional local LLM gateway (see deploy/litellm/config.yaml)
	docker compose --profile litellm up -d litellm
