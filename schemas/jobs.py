from pydantic import BaseModel
from datetime import datetime
from typing import List

# Esquema para crear un Puesto de Trabajo
class JobPositionCreate(BaseModel):
    title: str
    description: str

class JobPositionUpdate(BaseModel):
    title: str = None
    description: str = None


class JobPositionResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes = True
