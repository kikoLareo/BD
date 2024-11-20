from pydantic import BaseModel
from typing import Optional, Union  # Importa Union para tipos de unión

class DisciplineCreate(BaseModel):
    name: str
    category: Optional[str] = None

class DisciplineUpdate(BaseModel):
    name: Union[str, None]  # Sustituye el operador | con Union
    category: Optional[str] = None

class DisciplineResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True