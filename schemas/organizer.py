from pydantic import BaseModel
from typing import Optional, Union

class OrganizerCreate(BaseModel):
    name: str

class OrganizerUpdate(BaseModel):
    name: Union[str, None]  # Sustituye el operador | con Union

class OrganizerResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True