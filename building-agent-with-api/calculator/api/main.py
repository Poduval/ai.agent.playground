"""FastAPI calculator: add, subtract, multiply, divide. Protected by an API key."""

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException

from calculator import __version__
from calculator.api.operations import OPERATIONS
from calculator.api.schemas import Operands, Result
from calculator.config import get_settings
from common.security import api_key_auth

app = FastAPI(
    title="Calculator API",
    description="Four arithmetic operations on two numbers. Send `X-API-Key`.",
    version=__version__,
)

router = APIRouter(dependencies=[Depends(api_key_auth(lambda: get_settings().calculator_api_key))])


def _route(name: str):
    """Register POST /<name> for one operation."""

    @router.post(f"/{name}", response_model=Result, name=name, summary=f"{name.capitalize()} two numbers")
    def handler(operands: Operands) -> Result:
        try:
            return Result(operation=name, result=OPERATIONS[name](operands.a, operands.b))
        except ZeroDivisionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


for _name in OPERATIONS:
    _route(_name)

app.include_router(router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Public liveness probe (no API key)."""
    return {"status": "ok"}


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
