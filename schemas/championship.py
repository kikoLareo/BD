# schemas/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import List
from typing import Optional
from datetime import date


# Esquema para crear un Campeonato
class ChampionshipCreate(BaseModel):
    name: str
    location: int
    organizer_id: Optional[int] = None  # Permitir nulo
    discipline: Optional[int] = None  # Permitir nulo
    start_date: Optional[date] = None  # Permitir nulo
    end_date: Optional[date] = None  # Permitir nulo


class ChampionshipUpdate(BaseModel):
    name: str = None
    location: str = None
    organizer_id: str = None
    discipline: str = None
    start_date: date = None
    end_date: date = None


class ChampionshipDetailResponse(BaseModel):
    id: int
    name: str
    location: str
    organizer_id: Optional[str] = None  # Permitir nulo
    discipline: Optional[str] = None  # Permitir nulo
    start_date: Optional[date] = None  # Permitir nulo
    end_date: Optional[date] = None  # Permitir nulo

    class Config:
        orm_mode = True

