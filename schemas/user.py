from pydantic import BaseModel, EmailStr, Field

from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50, description="Nombre del usuario")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico del usuario")
    currentPassword: Optional[str] = Field(None, description="Contraseña actual para validación")
    newPassword: Optional[str] = Field(None, description="Nueva contraseña del usuario")
    confirmPassword: Optional[str] = Field(None, description="Confirmar nueva contraseña")

    class Config:
        schema_extra = {
            "example": {
                "username": "nuevo_usuario",
                "email": "nuevo_email@example.com",
                "currentPassword": "contraseña_actual",
                "newPassword": "nueva_contraseña",
                "confirmPassword": "nueva_contraseña"
            }
        }