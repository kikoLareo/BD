from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import User, Role, UserRole
from db.database import get_db
from schemas.user import UserCreate, UserResponse, UserUpdate
from schemas.role import RoleResponse
from logging_config import logger
from utils.hash import hash_password, verify_password
from typing import List
from db.CRUD.crud import get_user, create_new_user, get_all_users, update_user as update_user_crud, delete_user as delete_user_crud

router = APIRouter(
    prefix="/users",  # Prefijo para todas las rutas de este enrutador
    tags=["users"]
)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        logger.error(f"Usuario con ID {user_id} no encontrado")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# Endpoint para crear un nuevo usuario
@router.post("/create", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            logger.error("El usuario ya existe")
            raise HTTPException(status_code=400, detail="El usuario ya existe")

        hashed_password = hash_password(user_data.password)

        # Crear un nuevo usuario
        new_user = create_new_user(db, user_data.username, user_data.email, hashed_password)
        logger.info("Usuario creado exitosamente", extra={"component": "user_router", "user_id": new_user.id})
        return new_user
    except Exception as e:
        logger.error(f"Error al crear el usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para obtener todos los usuarios
@router.get("", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    try:
        users = get_all_users(db)
        logger.info("Usuarios obtenidos exitosamente")
        return users
    except Exception as e:
        logger.error(f"Error al obtener los usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{user_id}/update", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar la contraseña actual
    if not verify_password(user_data.currentPassword, user.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")

    # Actualizar contraseña si es necesario
    if user_data.newPassword:
        user.password_hash = hash_password(user_data.newPassword)

    # Actualizar otros campos
    user.username = user_data.username
    user.email = user_data.email
    db.commit()
    return user


# Endpoint para eliminar un usuario
@router.delete("/{user_id}/delete")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        response = delete_user_crud(db, user_id)
        logger.info(f"Usuario con ID {user_id} eliminado exitosamente")
        return response
    except ValueError as ve:
        logger.error(f"Error: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error al eliminar el usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para asignar un rol a un usuario
@router.post("/{user_id}/assign-role/{role_id}")
async def assign_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()

    if not user:
        logger.error(f"Usuario con ID {user_id} no encontrado")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not role:
        logger.error(f"Rol con ID {role_id} no encontrado")
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    # Verificar si el usuario ya tiene el rol
    user_role = db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).first()
    if user_role:
        logger.error(f"El usuario {user.username} ya tiene el rol {role.name} asignado")
        raise HTTPException(status_code=400, detail="El usuario ya tiene este rol asignado")

    # Asignar el rol al usuario
    new_user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(new_user_role)
    db.commit()
    logger.info(f"Se ha asignado el rol {role.name} al usuario {user.username}")
    return {"message": "Rol asignado exitosamente"}

# Endpoint para eliminar un rol de un usuario
@router.delete("/{user_id}/remove-role/{role_id}")
async def remove_role_from_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user_role = db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).first()

    if not user_role:
        logger.error("Rol no asignado al usuario")
        raise HTTPException(status_code=404, detail="Rol no asignado al usuario")

    db.delete(user_role)
    db.commit()
    logger.info(f"Se ha eliminado el rol {role_id} del usuario {user_id}")
    return {"message": "Rol eliminado del usuario"}