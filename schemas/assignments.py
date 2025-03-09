from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

# Esquema para la asignación de usuarios a campeonatos
class ChampionshipAssignmentCreate(BaseModel):
    user_id: int
    championship_id: int
    job_position_id: int
    hours_worked: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    username: Optional[str] = None
    job_position_name: Optional[str] = None
    championship_name: Optional[str] = None

class ChampionshipAssignmentUpdate(BaseModel):
    job_position_id: Optional[int] = None
    hours_worked: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    username: Optional[str] = None
    job_position_name: Optional[str] = None
    championship_name: Optional[str] = None

class ChampionshipAssignmentResponse(BaseModel):
    id: int
    user_id: int
    championship_id: int
    job_position_id: int
    hours_worked: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    username: Optional[str] = None
    job_position_name: Optional[str] = None
    championship_name: Optional[str] = None

    class Config:
        from_attributes = True
