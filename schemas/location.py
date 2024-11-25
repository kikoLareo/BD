from typing import Optional
from pydantic import BaseModel

class LocationCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    description: Optional[str]

class LocationResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    description: Optional[str]

    class Config:
        orm_mode = True