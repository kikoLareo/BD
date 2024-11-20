from pydantic import BaseModel
from datetime import datetime
from typing import List
from typing import Optional

# Esquema para crear un Puesto de Trabajo
class JobPositionCreate(BaseModel):
    title: str
    description: Optional[str] = None

class JobPositionUpdate(BaseModel):
    title: str = None
    description: Optional[str] = None


class JobPositionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]  # Cambiado a opcional

    class Config:
        from_attributes = True
