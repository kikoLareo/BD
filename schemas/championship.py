# schemas/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import List

# Esquema para crear un Campeonato
class ChampionshipCreate(BaseModel):
    name: str
    location: str
    date: datetime

class ChampionshipUpdate(BaseModel):
    name: str = None
    location: str = None
    date: datetime = None

class ChampionshipResponse(BaseModel):
    id: int
    name: str
    location: str
    date: datetime

    class Config:
        from_attributes = True


