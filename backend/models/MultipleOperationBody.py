from pydantic import BaseModel
from typing import List, Any


class SpecificOperationBody(BaseModel):
    operacion: str
    numeros: Any

class MultipleOperationBody(BaseModel):
    operaciones: List[SpecificOperationBody]

