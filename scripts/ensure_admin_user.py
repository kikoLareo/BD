#!/usr/bin/env python3
"""
Script para verificar si el usuario admin existe y crearlo si no existe.
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar los módulos necesarios
from db.database import get_db, engine, Base
from models.models import User, Role, UserRole
from utils.hash import hash_password
from logging_config import logger

# Cargar variables de entorno
load_dotenv()

def ensure_admin_user(db: Session, username: str, email: str, password: str, force: bool = False):
    """
    Verifica si el usuario admin existe y lo crea si no existe.
    
    Args:
        db (Session): Sesión de base de datos
        username (str): Nombre de usuario
        email (str): Email del usuario
        password (str): Contraseña del usuario
        force (bool): Si es True, actualiza el usuario aunque ya exista
    
    Returns:
        bool: True si se creó o actualizó el usuario, False si ya existía y no se actualizó
    """
    try:
        # Verificar si el usuario ya existe
        user = db.query(User).filter(User.username == username).first()
        
        if user:
            logger.info(f"El usuario {username} ya existe con ID: {user.id}")
            
            if force:
                logger.info(f"Actualizando usuario {username}...")
                user.email = email
                user.password_hash = hash_password(password)
                user.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Usuario {username} actualizado correctamente")
                return True
            else:
                logger.info(f"No se actualizó el usuario {username} (use --force para actualizar)")
                return False
        
        # Verificar si ya existe el rol "master"
        master_role = db.query(Role).filter(Role.name == "master").first()
        
        # Si no existe, crear el rol "master"
        if not master_role:
            logger.info("Creando rol 'master'...")
            master_role = Role(name="master", description="Usuario con todos los permisos")
            db.add(master_role)
            db.commit()
            db.refresh(master_role)
        
        # Crear el usuario
        logger.info(f"Creando usuario {username}...")
        hashed_password = hash_password(password)
        
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Asignar el rol "master" al usuario
        user_role = UserRole(user_id=new_user.id, role_id=master_role.id)
        db.add(user_role)
        db.commit()
        
        logger.info(f"Usuario {username} creado correctamente con ID: {new_user.id}")
        return True
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos: {str(e)}")
        return False
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Verifica si el usuario admin existe y lo crea si no existe")
    parser.add_argument("--username", default=os.getenv("MASTER_USERNAME", "admin"),
                        help="Nombre de usuario (default: valor de MASTER_USERNAME o admin)")
    parser.add_argument("--email", default=os.getenv("MASTER_EMAIL", "admin@wavestudio.com"),
                        help="Email del usuario (default: valor de MASTER_EMAIL o admin@wavestudio.com)")
    parser.add_argument("--password", default=os.getenv("MASTER_PASSWORD", "admin123"),
                        help="Contraseña del usuario (default: valor de MASTER_PASSWORD o admin123)")
    parser.add_argument("--force", action="store_true",
                        help="Actualizar el usuario aunque ya exista")
    
    args = parser.parse_args()
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    # Obtener una sesión de base de datos
    db = next(get_db())
    try:
        # Verificar si el usuario admin existe y crearlo si no existe
        success = ensure_admin_user(db, args.username, args.email, args.password, args.force)
        
        if success:
            print(f"✅ Usuario {args.username} creado o actualizado correctamente")
            sys.exit(0)
        else:
            print(f"ℹ️ El usuario {args.username} ya existe y no se actualizó")
            sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
