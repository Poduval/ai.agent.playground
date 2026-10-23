"""API-key auth for the REST APIs: a FastAPI dependency checking `X-API-Key`."""

import hmac
from collections.abc import Callable

from fastapi import Header, HTTPException


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
