from pydantic import BaseModel
from typing import List, Optional

class AsciiValueInput(BaseModel):
    text: str

class ExponentialSumInput(BaseModel):
    ascii_values: List[int]

class ReasoningStepsInputs(BaseModel):
    steps: List[str]


class OperationValueOutput(BaseModel):
    type: str = "text"
    text: str

class AddInput(BaseModel):
    a: int
    b: int

class AddOutput(BaseModel):
    result: int




