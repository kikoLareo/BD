from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import Role
from schemas.role import RoleCreate, RoleResponse, RoleUpdate
from db.database import get_db
from logging_config import logger
from db.CRUD.rolesCrud import get_all_roles, create_new_role, get_role

router = APIRouter(
    prefix="/roles",  # Prefijo para todas las rutas de este enrutador
    tags=["roles"]
)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role_by_id(role_id: int, db: Session = Depends(get_db)):
    role = get_role(db, role_id)
    if not role:
        logger.error(f"Rol no encontrado con ID {role_id}")
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


# Endpoint para obtener todos los roles
@router.get("", response_model=list[RoleResponse])
async def get_roles(db: Session = Depends(get_db)):
    try:
        roles = get_all_roles(db)  # Reutiliza la lógica de rolesCrud
        logger.info("Roles obtenidos exitosamente")
        return roles
    except Exception as e:
        logger.error(f"Error al obtener los roles: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los roles")

# Endpoint para crear un nuevo rol
@router.post("/create", response_model=RoleResponse)
async def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        logger.error(f"El rol '{role_data.name}' ya existe")
        raise HTTPException(status_code=400, detail="El rol ya existe")

    try:
        # Crea el nuevo rol sin especificar id (el id se generará automáticamente)
        new_role = create_new_role(db, role_data.name, role_data.description)
        logger.info(f"Rol creado: {new_role.name} con ID {new_role.id}")
        return new_role  # Se devolverá como RoleResponse
    except Exception as e:
        logger.error(f"Error al crear el rol: {e}")
        raise HTTPException(status_code=500, detail="Error al crear el rol")

# Endpoint para actualizar un rol
@router.put("/update/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        logger.error(f"Rol no encontrado con ID {role_id}")
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    if role_data.name:
        role.name = role_data.name
    if role_data.description:
        role.description = role_data.description

    try:
        db.commit()
        db.refresh(role)
        logger.info(f"Rol actualizado: {role.name} con ID {role.id}")
        return role  # Se devolverá como RoleResponse
    except Exception as e:
        db.rollback()  # Revertir la transacción en caso de error
        logger.error(f"Error al actualizar el rol con ID {role_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar el rol")

# Endpoint para eliminar un rol
@router.delete("/delete/{role_id}", response_model=dict)
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        logger.error(f"Rol no encontrado con ID {role_id}")
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    try:
        db.delete(role)
        db.commit()
        logger.info(f"Rol eliminado: {role.name} con ID {role.id}")
        return {"message": "Rol eliminado exitosamente"}
    except Exception as e:
        db.rollback()  # Revertir la transacción en caso de error
        logger.error(f"Error al eliminar el rol con ID {role_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar el rol")