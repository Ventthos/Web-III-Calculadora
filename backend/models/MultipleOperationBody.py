from pydantic import BaseModel
from typing import List

class SpecificOperationBody(BaseModel):
    operacion: str
    numeros: List[float]

class MultipleOperationBody(BaseModel):
    operaciones: List[SpecificOperationBody]

