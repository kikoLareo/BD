from pydantic import BaseModel
from datetime import datetime
from typing import List
from typing import Optional

# Esquema para crear un Puesto de Trabajo
class JobPositionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cost_per_day: float
    cost_per_hour: float = None

class JobPositionUpdate(BaseModel):
    title: str = None
    description: Optional[str] = None
    cost_per_day: float = None
    cost_per_hour: float = None



class JobPositionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]  # Cambiado a opcional
    cost_per_day: float
    cost_per_hour: float = None

    class Config:
        from_attributes = True

