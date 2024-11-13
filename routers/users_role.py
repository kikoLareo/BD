from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import User, UserRole, Role
from db.database import get_db
from logging_config import logger
router = APIRouter()

# Endpoint para asignar un rol a un usuario
@router.post("/users/{user_id}/assign-role/{role_id}")
async def assign_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()

    if not user:
        logger.error("Usuario no encontrado")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not role:
        logger.error("Rol no encontrado")
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    db.commit()
    logger.info("Se ha asignado el rol {role.name} al usuario {user.username}")
    return {"message": "Rol asignado exitosamente"}

# Endpoint para eliminar un rol de un usuario
@router.delete("/users/{user_id}/remove-role/{role_id}")
async def remove_role_from_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user_role = db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).first()
    if not user_role:
        logger.error("Rol no asignado al usuario")
        raise HTTPException(status_code=404, detail="Rol no asignado al usuario")

    db.delete(user_role)
    db.commit()
    logger.info("Se ha eliminado el rol {role.name} del usuario {user.username}")
    return {"message": "Rol eliminado del usuario"}
