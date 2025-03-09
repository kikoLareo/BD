from pydantic import BaseModel
from typing import Optional, Union

class OrganizerCreate(BaseModel):
    name: str
    description: Optional[str] = None
    placement: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class OrganizerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    placement: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class OrganizerResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    placement: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    class Config:
        from_attributes = True
