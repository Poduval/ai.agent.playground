"""Assemble the A2A application: Agent Card route + JSON-RPC route + bearer-token auth.

Run: `calculator-a2a`  (http://127.0.0.1:8002)
"""

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from starlette.applications import Starlette
from starlette.middleware import Middleware

from calculator.a2a.card import build_agent_card
from calculator.a2a.executor import CalculatorExecutor
from calculator.config import Settings, get_settings
from common.security import BearerTokenMiddleware


def build_app(settings: Settings | None = None, executor: CalculatorExecutor | None = None) -> Starlette:
    settings = settings or get_settings()
    card = build_agent_card(settings)
    handler = DefaultRequestHandler(
        agent_executor=executor or CalculatorExecutor(),
        task_store=InMemoryTaskStore(),  # swap for a persistent store in production
        agent_card=card,
    )
    routes = create_agent_card_routes(card) + create_jsonrpc_routes(handler, rpc_url="/")
    return Starlette(routes=routes, middleware=[Middleware(BearerTokenMiddleware, token=settings.a2a_bearer_token)])


def main() -> None:
    uvicorn.run(build_app(), host="127.0.0.1", port=8002)


if __name__ == "__main__":
    main()
