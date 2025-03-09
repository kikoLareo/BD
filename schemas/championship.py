# schemas/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import List
from typing import Optional
from datetime import date


# Esquema para crear un Campeonato
class ChampionshipCreate(BaseModel):
    name: str
    location: Optional[str] = None  # Permitir nulo
    organizer_id: Optional[int] = None  # Permitir nulo
    discipline_id: Optional[int] = None  # Permitir nulo
    start_date: Optional[date] = None  # Permitir nulo
    end_date: Optional[date] = None  # Permitir nulo
    description: Optional[str] = None  # Permitir nulo


class ChampionshipUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    organizer_id: Optional[int] = None
    discipline_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class ChampionshipDetailResponse(BaseModel):
    id: int
    name: str
    location: Optional[str] = None  # Permitir nulo
    organizer_id: Optional[int] = None  # Permitir nulo
    organizer_name: Optional[str] = None  # Permitir nulo
    discipline_id: Optional[int] = None  # Permitir nulo
    discipline_name: Optional[str] = None  # Permitir nulo
    start_date: Optional[date] = None  # Permitir nulo
    end_date: Optional[date] = None  # Permitir nulo
    description: Optional[str] = None  # Permitir nulo

    class Config:
        orm_mode = True
