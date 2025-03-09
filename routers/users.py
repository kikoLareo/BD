from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.models import User, Role, UserRole
from db.database import get_db
from schemas.user import UserCreate, UserResponse, UserUpdate, UserCreateByMaster
from schemas.role import RoleResponse
from logging_config import logger
from utils.hash import hash_password, verify_password
from typing import List, Optional
from db.CRUD.crud import get_user, create_new_user, get_all_users, update_user as update_user_crud, delete_user as delete_user_crud
from JWT.verToken import get_current_user, is_master_user, check_user_role
from datetime import datetime

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = get_user(db, user_id)
    if not user:
        logger.error(f"Usuario con ID {user_id} no encontrado")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Endpoint para crear un nuevo usuario (solo para usuarios Master)
@router.post("/create", response_model=UserResponse)
async def create_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(is_master_user)
):
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
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        users = get_all_users(db)
        logger.info("Usuarios obtenidos exitosamente")
        return users
    except Exception as e:
        logger.error(f"Error al obtener los usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{user_id}/update", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar si el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si es el propio usuario o un usuario Master
    is_master = False
    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role and role.name == "master":
            is_master = True
            break
    
    if current_user.id != user_id and not is_master:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )
    
    # Si no es un usuario Master, validar la contraseña actual
    if not is_master and user_data.currentPassword:
        if not verify_password(user_data.currentPassword, user.password_hash):
            raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    
    # Actualizar contraseña si es necesario
    if user_data.newPassword:
        if user_data.newPassword != user_data.confirmPassword:
            raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
        user.password_hash = hash_password(user_data.newPassword)
    
    # Actualizar otros campos si se proporcionan
    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = user_data.email
    
    # Actualizar timestamp
    user.updated_at = datetime.utcnow()
    
    db.commit()
    logger.info(f"Usuario {user.username} actualizado por {current_user.username}")
    return user

# Endpoint para que un usuario Master cree un nuevo usuario
@router.post("/master/create", response_model=UserResponse)
async def create_user_by_master(
    user_data: UserCreateByMaster,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_master_user)
):
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            logger.error("El usuario ya existe")
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        
        # Hashear la contraseña
        hashed_password = hash_password(user_data.password)
        
        # Crear un nuevo usuario
        new_user = create_new_user(
            db, 
            user_data.username, 
            user_data.email, 
            hashed_password
        )
        
        # Asignar roles si se proporcionan
        if user_data.roles:
            for role_id in user_data.roles:
                role = db.query(Role).filter(Role.id == role_id).first()
                if not role:
                    logger.warning(f"Rol con ID {role_id} no encontrado")
                    continue
                
                # Verificar si ya tiene el rol asignado
                existing_role = db.query(UserRole).filter(
                    UserRole.user_id == new_user.id,
                    UserRole.role_id == role_id
                ).first()
                
                if not existing_role:
                    new_user_role = UserRole(user_id=new_user.id, role_id=role_id)
                    db.add(new_user_role)
        
        db.commit()
        logger.info(f"Usuario {new_user.username} creado por el usuario Master {current_user.username}")
        return new_user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear el usuario: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Endpoint para cambiar la contraseña de un usuario (solo para usuarios Master)
@router.put("/{user_id}/change-password")
async def change_user_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_master_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Hashear y actualizar la contraseña
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    
    db.commit()
    logger.info(f"Contraseña del usuario {user.username} cambiada por el usuario Master {current_user.username}")
    
    return {"message": "Contraseña actualizada exitosamente"}


# Endpoint para eliminar un usuario (solo para usuarios Master)
@router.delete("/{user_id}/delete")
async def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(is_master_user)
):
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

# Endpoint para asignar un rol a un usuario (solo para usuarios Master)
@router.post("/{user_id}/assign-role/{role_id}")
async def assign_role_to_user(
    user_id: int, 
    role_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(is_master_user)
):
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

# Endpoint para eliminar un rol de un usuario (solo para usuarios Master)
@router.delete("/{user_id}/remove-role/{role_id}")
async def remove_role_from_user(
    user_id: int, 
    role_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(is_master_user)
):
    user_role = db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).first()

    if not user_role:
        logger.error("Rol no asignado al usuario")
        raise HTTPException(status_code=404, detail="Rol no asignado al usuario")

    db.delete(user_role)
    db.commit()
    logger.info(f"Se ha eliminado el rol {role_id} del usuario {user_id}")
    return {"message": "Rol eliminado del usuario"}
