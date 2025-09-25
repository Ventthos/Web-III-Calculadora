from pydantic import BaseModel
from typing import List

class SingleOperationBody(BaseModel):
    numeros: List[float]