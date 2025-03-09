from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: str = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

class UserCreateByMaster(UserCreate):
    roles: Optional[List[int]] = Field(None, description="Lista de IDs de roles a asignar")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    roles: Optional[List[Dict[str, Any]]] = None

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Nombre del usuario")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico del usuario")
    currentPassword: Optional[str] = Field(None, description="Contraseña actual para validación")
    newPassword: Optional[str] = Field(None, min_length=6, description="Nueva contraseña del usuario")
    confirmPassword: Optional[str] = Field(None, description="Confirmar nueva contraseña")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "nuevo_usuario",
                "email": "nuevo_email@example.com",
                "currentPassword": "contraseña_actual",
                "newPassword": "nueva_contraseña",
                "confirmPassword": "nueva_contraseña"
            }
        }

class ChangePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
