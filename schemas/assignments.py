from pydantic import BaseModel
from datetime import datetime
from typing import List

# Esquema para la asignación de usuarios a campeonatos
class ChampionshipAssignmentCreate(BaseModel):
    user_id: int
    championship_id: int
    job_position_id: int
    hours_worked: float

class ChampionshipAssignmentUpdate(BaseModel):
    job_position_id: int = None
    hours_worked: float = None

class ChampionshipAssignmentResponse(BaseModel):
    user_id: int
    championship_id: int
    job_position_id: int
    hours_worked: float

    class Config:
        from_attributes = True