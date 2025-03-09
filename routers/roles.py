from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models.models import Role
from schemas.role import RoleCreate, RoleResponse, RoleUpdate
from db.database import get_db
from logging_config import logger
from db.CRUD.rolesCrud import get_all_roles, create_new_role, get_role
from utils.error_handling import (
    handle_exceptions, 
    CommonErrors, 
    APIError, 
    ErrorCodes
)

router = APIRouter(
    prefix="/roles",  # Prefijo para todas las rutas de este enrutador
    tags=["roles"]
)


@router.get("/{role_id}", response_model=RoleResponse)
@handle_exceptions
async def get_role_by_id(role_id: int, db: Session = Depends(get_db)):
    role = get_role(db, role_id)
    if not role:
        logger.error(f"Rol no encontrado con ID {role_id}")
        raise CommonErrors.not_found("Rol", role_id)
    return role


# Endpoint para obtener todos los roles
@router.get("", response_model=list[RoleResponse])
@handle_exceptions
async def get_roles(db: Session = Depends(get_db)):
    roles = get_all_roles(db)  # Reutiliza la lógica de rolesCrud
    logger.info("Roles obtenidos exitosamente")
    return roles

# Endpoint para crear un nuevo rol
@router.post("/create", response_model=RoleResponse)
@handle_exceptions
async def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    # Verificar si el rol ya existe
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        logger.error(f"El rol '{role_data.name}' ya existe")
        raise CommonErrors.already_exists("Rol", f"nombre '{role_data.name}'")

    try:
        # Crea el nuevo rol sin especificar id (el id se generará automáticamente)
        new_role = create_new_role(db, role_data.name, role_data.description)
        logger.info(f"Rol creado: {new_role.name} con ID {new_role.id}")
        return new_role  # Se devolverá como RoleResponse
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al crear rol: {str(e)}")
        raise CommonErrors.database_error(f"Error al crear el rol: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear rol: {str(e)}")
        raise CommonErrors.internal_error(f"Error al crear el rol: {str(e)}")

# Endpoint para actualizar un rol
@router.put("/update/{role_id}", response_model=RoleResponse)
@handle_exceptions
async def update_role(role_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    # Verificar si el rol existe
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        logger.error(f"Rol no encontrado con ID {role_id}")
        raise CommonErrors.not_found("Rol", role_id)
    
    # Verificar si el nuevo nombre ya existe (si se está cambiando)
    if role_data.name and role_data.name != role.name:
        existing_role = db.query(Role).filter(Role.name == role_data.name).first()
        if existing_role:
            logger.error(f"Ya existe un rol con el nombre '{role_data.name}'")
            raise CommonErrors.already_exists("Rol", f"nombre '{role_data.name}'")
    
    try:
        # Actualizar los campos
        if role_data.name:
            role.name = role_data.name
        if role_data.description:
            role.description = role_data.description

        db.commit()
        db.refresh(role)
        logger.info(f"Rol actualizado: {role.name} con ID {role.id}")
        return role  # Se devolverá como RoleResponse
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al actualizar rol: {str(e)}")
        raise CommonErrors.database_error(f"Error al actualizar el rol: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar rol: {str(e)}")
        raise CommonErrors.internal_error(f"Error al actualizar el rol: {str(e)}")

# Endpoint para eliminar un rol
@router.delete("/delete/{role_id}", response_model=dict)
@handle_exceptions
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    # Verificar si el rol existe
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        logger.error(f"Rol no encontrado con ID {role_id}")
        raise CommonErrors.not_found("Rol", role_id)

    try:
        # Eliminar el rol
        db.delete(role)
        db.commit()
        logger.info(f"Rol eliminado: {role.name} con ID {role.id}")
        return {"message": "Rol eliminado exitosamente", "code": "SUCCESS"}
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar rol: {str(e)}")
        raise APIError(
            code=ErrorCodes.INTEGRITY_ERROR,
            message="No se puede eliminar el rol porque está en uso",
            status_code=400,
            details="Este rol está asignado a uno o más usuarios. Elimine primero estas asignaciones."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al eliminar rol: {str(e)}")
        raise CommonErrors.database_error(f"Error al eliminar el rol: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al eliminar rol: {str(e)}")
        raise CommonErrors.internal_error(f"Error al eliminar el rol: {str(e)}")
