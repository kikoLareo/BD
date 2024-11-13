from sqlalchemy.orm import Session
from models import models
from logging_config import logger

# Obtener un rol por ID
def get_role(db: Session, role_id: int):
    try:
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if role:
            logger.info(f"Rol con ID {role_id} encontrado: {role.name}")
        else:
            logger.warning(f"Rol con ID {role_id} no encontrado")
        return role
    except Exception as e:
        logger.error(f"Error al obtener el rol con ID {role_id}: {e}")
        raise

# Obtener todos los roles
def get_all_roles(db: Session):
    try:
        roles = db.query(models.Role).all()
        logger.info(f"Se han recuperado {len(roles)} roles de la base de datos")
        return roles
    except Exception as e:
        logger.error(f"Error al obtener todos los roles: {e}")
        raise

# Crear un nuevo rol
def create_new_role(db: Session, name: str, description: str):
    try:
        role = models.Role(name=name, description=description)
        db.add(role)
        db.commit()
        db.refresh(role)
        logger.info(f"Rol '{role.name}' creado exitosamente con ID {role.id}")
        return role
    except Exception as e:
        db.rollback()  # Revertir la transacción en caso de error
        logger.error(f"Error al crear el rol en la base de datos: {e}")
        raise

# Actualizar un rol existente
def update_role(db: Session, role_id: int, name: str, description: str):
    try:
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not role:
            logger.error(f"Rol con ID {role_id} no encontrado")
            raise ValueError(f"Rol con ID {role_id} no encontrado")

        # Actualizar los campos
        role.name = name
        role.description = description
        db.commit()
        logger.info(f"Rol con ID {role_id} actualizado exitosamente: {role.name}")
        return role
    except Exception as e:
        db.rollback()  # Revertir la transacción en caso de error
        logger.error(f"Error al actualizar el rol con ID {role_id}: {e}")
        raise

# Eliminar un rol
def delete_role(db: Session, role_id: int):
    try:
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not role:
            logger.error(f"Rol con ID {role_id} no encontrado")
            raise ValueError(f"Rol con ID {role_id} no encontrado")

        db.delete(role)
        db.commit()
        logger.info(f"Rol con ID {role_id} eliminado exitosamente")
        return {"message": "Rol eliminado exitosamente"}
    except Exception as e:
        db.rollback()  # Revertir la transacción en caso de error
        logger.error(f"Error al eliminar el rol con ID {role_id}: {e}")
        raise