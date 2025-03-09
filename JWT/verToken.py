from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import User, UserRole, Role
from JWT.tokens import SECRET_KEY, ALGORITHM
from typing import List
from logging_config import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_user(db: Session, username: str):
    """Obtiene un usuario por su nombre de usuario"""
    return db.query(User).filter(User.username == username).first()

def get_user_roles(db: Session, user_id: int) -> List[Role]:
    """Obtiene los roles de un usuario"""
    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    roles = []
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            roles.append(role)
    return roles

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Verifica el token JWT y devuelve el usuario actual.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token sin nombre de usuario")
            raise credentials_exception
        
        # Obtener información adicional del token
        user_id: int = payload.get("user_id")
        role_ids: List[int] = payload.get("roles", [])
        
    except JWTError as e:
        logger.error(f"Error al decodificar el token: {e}")
        raise credentials_exception
    
    # Obtener el usuario de la base de datos
    user = get_user(db, username=username)
    if user is None:
        logger.warning(f"Usuario {username} no encontrado en la base de datos")
        raise credentials_exception
    
    # Añadir información de roles al objeto usuario
    user.role_ids = role_ids
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Verifica que el usuario esté activo.
    """
    # Aquí podrías verificar si el usuario está activo en caso de tener ese campo
    return current_user

def check_user_role(required_roles: List[str]):
    """
    Dependencia para verificar si el usuario tiene alguno de los roles requeridos.
    """
    async def role_checker(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        user_roles = get_user_roles(db, current_user.id)
        user_role_names = [role.name for role in user_roles]
        
        # Verificar si el usuario tiene alguno de los roles requeridos
        for role in required_roles:
            if role in user_role_names:
                return current_user
        
        logger.warning(f"Usuario {current_user.username} intentó acceder a una ruta protegida sin los roles necesarios")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este recurso"
        )
    async def role_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        user_roles = get_user_roles(db, current_user.id)
        user_role_names = [role.name for role in user_roles]
        
        # Verificar si el usuario tiene alguno de los roles requeridos
        for role in required_roles:
            if role in user_role_names:
                return current_user
        
        logger.warning(f"Usuario {current_user.username} intentó acceder a una ruta protegida sin los roles necesarios")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este recurso"
        )
    
    return role_checker

def is_master_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Verifica si el usuario es un usuario Master.
    """
    user_roles = get_user_roles(db, current_user.id)
    user_role_names = [role.name for role in user_roles]
    
    if "master" in user_role_names:
        return current_user
    
    logger.warning(f"Usuario {current_user.username} intentó acceder a una función de Master")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Solo los usuarios Master pueden realizar esta acción"
    )
