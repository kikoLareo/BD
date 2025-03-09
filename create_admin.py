from sqlalchemy.orm import Session
from db.database import engine, SessionLocal, Base
from models.models import User, Role, UserRole
from utils.hash import hash_password
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_master_user():
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # Verificar si ya existe el rol "master"
        master_role = session.query(Role).filter(Role.name == "master").first()
        
        # Si no existe, crear el rol "master"
        if not master_role:
            print("Creando rol 'master'...")
            master_role = Role(name="master", description="Usuario con todos los permisos")
            session.add(master_role)
            session.commit()
            session.refresh(master_role)
            print(f"Rol 'master' creado con ID: {master_role.id}")
        else:
            print(f"El rol 'master' ya existe con ID: {master_role.id}")
        
        # Obtener credenciales desde variables de entorno
        master_username = os.getenv("MASTER_USERNAME", "admin")
        master_email = os.getenv("MASTER_EMAIL", "admin@wavestudio.com")
        master_password = os.getenv("MASTER_PASSWORD", "admin123")
        
        # Verificar si ya existe el usuario admin
        admin_user = session.query(User).filter(User.username == master_username).first()
        
        if not admin_user:
            print(f"Creando usuario Master: {master_username}")
            hashed_password = hash_password(master_password)
            
            admin_user = User(
                username=master_username,
                email=master_email,
                password_hash=hashed_password,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            print(f"Usuario Master creado con ID: {admin_user.id}")
            
            # Asignar el rol "master" al usuario
            user_role = UserRole(user_id=admin_user.id, role_id=master_role.id)
            session.add(user_role)
            session.commit()
            print(f"Rol 'master' asignado al usuario '{master_username}'")
        else:
            print(f"El usuario '{master_username}' ya existe con ID: {admin_user.id}")
            
            # Verificar si ya tiene el rol master
            user_role = session.query(UserRole).filter(
                UserRole.user_id == admin_user.id,
                UserRole.role_id == master_role.id
            ).first()
            
            if not user_role:
                user_role = UserRole(user_id=admin_user.id, role_id=master_role.id)
                session.add(user_role)
                session.commit()
                print(f"Rol 'master' asignado al usuario '{master_username}'")
            else:
                print(f"El usuario '{master_username}' ya tiene el rol 'master'")
        
        # Mostrar todos los usuarios y roles
        print("\nUsuarios en la base de datos:")
        users = session.query(User).all()
        for user in users:
            print(f"- {user.username} (ID: {user.id}, Email: {user.email})")
        
        print("\nRoles en la base de datos:")
        roles = session.query(Role).all()
        for role in roles:
            print(f"- {role.name} (ID: {role.id}, Descripción: {role.description})")
        
        print("\nAsignaciones de roles a usuarios:")
        user_roles = session.query(UserRole).all()
        for ur in user_roles:
            user = session.query(User).filter(User.id == ur.user_id).first()
            role = session.query(Role).filter(Role.id == ur.role_id).first()
            if user and role:
                print(f"- Usuario '{user.username}' tiene rol '{role.name}'")
    
    finally:
        session.close()

if __name__ == "__main__":
    create_master_user()
