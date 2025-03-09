from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import get_db
from models.models import User, UserRole
from schemas.pydantic import Token, UserLogin
from utils.hash import verify_password
from JWT.tokens import create_access_token
from datetime import timedelta
from logging_config import logger
from utils.error_handling import (
    handle_exceptions, 
    CommonErrors, 
    APIError, 
    ErrorCodes
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/token", response_model=Token)
@handle_exceptions
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint para autenticar usuarios y generar un token JWT.
    """
    try:
        # Buscar usuario por nombre de usuario
        user = db.query(User).filter(User.username == form_data.username).first()
        
        # Si no existe el usuario o la contraseña es incorrecta
        if not user or not verify_password(form_data.password, user.password_hash):
            logger.warning(f"Intento de login fallido para el usuario: {form_data.username}")
            raise APIError(
                code=ErrorCodes.INVALID_CREDENTIALS,
                message="Credenciales inválidas",
                status_code=status.HTTP_401_UNAUTHORIZED,
                details="El nombre de usuario o la contraseña son incorrectos"
            )
        
        # Obtener roles del usuario
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        role_ids = [user_role.role_id for user_role in user_roles]
        
        # Crear datos para el token
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "roles": role_ids
        }
        
        # Generar token con duración de 12 semanas
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(weeks=12)
        )
        
        logger.info(f"Login exitoso para el usuario: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except APIError:
        # Reenviar errores de API ya manejados
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos durante la autenticación: {str(e)}")
        raise CommonErrors.database_error(f"Error durante la autenticación: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado durante la autenticación: {str(e)}")
        raise CommonErrors.internal_error(f"Error durante la autenticación: {str(e)}")

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint alternativo para login que acepta JSON en lugar de form-data.
    """
    try:
        # Obtener los datos del cuerpo de la solicitud directamente
        body = await request.json()
        logger.info(f"Datos de login recibidos: {body}")
        
        # Validar que los datos requeridos estén presentes
        username = body.get("username")
        password = body.get("password")
        
        if not username or not password:
            logger.warning("Intento de login con datos incompletos")
            raise APIError(
                code=ErrorCodes.MISSING_FIELDS,
                message="Datos incompletos",
                status_code=status.HTTP_400_BAD_REQUEST,
                details="El nombre de usuario y la contraseña son obligatorios"
            )
            
        logger.info(f"Intento de login para el usuario: {username}")
        # Buscar usuario por nombre de usuario
        user = db.query(User).filter(User.username == username).first()
        
        # Si no existe el usuario o la contraseña es incorrecta
        if not user or not verify_password(password, user.password_hash):
            logger.warning(f"Intento de login fallido para el usuario: {username}")
            raise APIError(
                code=ErrorCodes.INVALID_CREDENTIALS,
                message="Credenciales inválidas",
                status_code=status.HTTP_401_UNAUTHORIZED,
                details="El nombre de usuario o la contraseña son incorrectos"
            )
        
        # Obtener roles del usuario
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        role_ids = [user_role.role_id for user_role in user_roles]
        
        # Crear datos para el token
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "roles": role_ids
        }
        
        # Generar token con duración de 12 semanas
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(weeks=12)
        )
        
        logger.info(f"Login exitoso para el usuario: {user.username}")
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": role_ids
            }
        }
    except APIError:
        # Reenviar errores de API ya manejados
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos durante la autenticación: {str(e)}")
        raise CommonErrors.database_error(f"Error durante la autenticación: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado durante la autenticación: {str(e)}")
        raise CommonErrors.internal_error(f"Error durante la autenticación: {str(e)}")
