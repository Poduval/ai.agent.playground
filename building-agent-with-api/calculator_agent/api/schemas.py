"""Request and response models; FastAPI turns these into validation and OpenAPI docs."""

from pydantic import BaseModel, Field


class Operands(BaseModel):
    # allow_inf_nan=False rejects NaN/Infinity so results stay meaningful.
    a: float = Field(allow_inf_nan=False, examples=[6])
    b: float = Field(allow_inf_nan=False, examples=[7])


class Result(BaseModel):
    operation: str
    result: float
