from pydantic import BaseModel
from typing import Literal


class BaseOut(BaseModel):
    out_type: str

class EntityState(BaseModel):
    out_type: Literal['entity'] = 'entity'
    entity_type: str