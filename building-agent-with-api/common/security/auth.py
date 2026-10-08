"""Two small, readable auth mechanisms.

* REST API  -> API key in the `X-API-Key` header (a FastAPI dependency).
* A2A agent -> bearer token in `Authorization` (an ASGI middleware), matching the
  security scheme advertised in the Agent Card.
"""

import hmac
from collections.abc import Callable

from fastapi import Header, HTTPException
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


def _matches(supplied: str | None, expected: str) -> bool:
    # compare_digest avoids leaking the secret through response timing.
    return bool(supplied) and hmac.compare_digest(supplied.encode(), expected.encode())


def api_key_auth(expected_key: Callable[[], str]) -> Callable[..., None]:
    """Build a FastAPI dependency that requires `X-API-Key` to equal `expected_key()`.

    Passing a function (not a string) means the key is read at request time from settings.
    """

    def dependency(x_api_key: str | None = Header(default=None)) -> None:
        if not _matches(x_api_key, expected_key()):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

    return dependency


class BearerTokenMiddleware:
    """Require `Authorization: Bearer <token>` except on public paths (the Agent Card)."""

    def __init__(self, app: ASGIApp, token: str, public_prefixes: tuple[str, ...] = ("/.well-known/",)):
        self.app = app
        self.token = token
        self.public_prefixes = public_prefixes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"].startswith(self.public_prefixes):
            await self.app(scope, receive, send)
            return
        headers = dict(scope["headers"])
        supplied = headers.get(b"authorization", b"").decode().removeprefix("Bearer ").strip()
        if not _matches(supplied, self.token):
            response = JSONResponse(
                {"error": "Missing or invalid bearer token"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)
