.PHONY: install test lint api mcp a2a redis litellm

install:        ## create .venv and install with dev tools
	python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
test:
	.venv/bin/pytest
lint:
	.venv/bin/ruff check calculator_agent tests
api:            ## terminal 1
	.venv/bin/calculator-api
mcp:            ## terminal 2
	.venv/bin/calculator-mcp
a2a:            ## terminal 3
	.venv/bin/calculator-a2a
redis:          ## optional memory backend
	docker compose up -d redis
litellm:        ## optional local LLM gateway (see deploy/litellm/config.yaml)
	docker compose --profile litellm up -d litellm
