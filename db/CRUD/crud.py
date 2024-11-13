from sqlalchemy.orm import Session
from models import models
from logging_config import logger

# Función para obtener un usuario por ID
def get_user(db: Session, user_id: int):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            logger.info(f"Usuario con ID {user_id} encontrado")
        else:
            logger.warning(f"Usuario con ID {user_id} no encontrado")
        return user
    except Exception as e:
        logger.error(f"Error al obtener el usuario con ID {user_id}: {e}")
        raise

# Función para obtener todos los usuarios
def get_all_users(db: Session):
    try:
        users = db.query(models.User).all()
        logger.info(f"Se han recuperado {len(users)} usuarios de la base de datos")
        return users
    except Exception as e:
        logger.error(f"Error al obtener todos los usuarios: {e}")
        raise

# Función para crear un nuevo usuario
def create_new_user(db: Session, username: str, email: str, password_hash: str):
    try:
        user = models.User(username=username, email=email, password_hash=password_hash)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Usuario '{user.username}' creado exitosamente con ID {user.id}")
        return user
    except Exception as e:
        db.rollback()  # Revertir la transacción si hay un error
        logger.error(f"Error al crear el usuario en la base de datos: {e}")
        raise

# Función para actualizar un usuario
def update_user(db: Session, user_id: int, username: str, email: str):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.error(f"Usuario con ID {user_id} no encontrado")
            raise ValueError(f"Usuario con ID {user_id} no encontrado")
        
        # Actualizar campos
        user.username = username
        user.email = email
        db.commit()
        logger.info(f"Usuario con ID {user_id} actualizado exitosamente")
        return user
    except Exception as e:
        db.rollback()  # Revertir la transacción si hay un error
        logger.error(f"Error al actualizar el usuario con ID {user_id}: {e}")
        raise

# Función para eliminar un usuario
def delete_user(db: Session, user_id: int):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.error(f"Usuario con ID {user_id} no encontrado")
            raise ValueError(f"Usuario con ID {user_id} no encontrado")
        
        db.delete(user)
        db.commit()
        logger.info(f"Usuario con ID {user_id} eliminado exitosamente")
        return {"message": "Usuario eliminado exitosamente"}
    except Exception as e:
        db.rollback()  # Revertir la transacción si hay un error
        logger.error(f"Error al eliminar el usuario con ID {user_id}: {e}")
        raise