.PHONY: install test lint calculator-api calculator-mcp

install:        ## create .venv and install with dev tools
	python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
test:
	.venv/bin/pytest
lint:
	.venv/bin/ruff check common calculator tests
calculator-api: ## REST API on :8000
	.venv/bin/calculator-api
calculator-mcp: ## MCP server on :8001/mcp (needs the API running)
	.venv/bin/calculator-mcp
