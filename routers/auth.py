from fastapi import APIRouter, Depends, status, Request, HTTPException
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"Usuario encontrado: {user.username}")
        
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
        try:
            body = await request.json()
            logger.info(f"Datos de login recibidos: {body}")
        except Exception as e:
            logger.error(f"Error al parsear el cuerpo de la solicitud: {str(e)}")
            logger.error(f"Contenido de la solicitud: {await request.body()}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al procesar la solicitud",
                headers={"Content-Type": "application/json"}
            )
        
        # Validar que los datos requeridos estén presentes
        username = body.get("username")
        password = body.get("password")
        
        logger.info(f"Validando credenciales - Username: {username}, Password: {'*' * len(password) if password else 'None'}")
        
        if not username or not password:
            logger.warning("Intento de login con datos incompletos")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de usuario y contraseña son requeridos",
                headers={"Content-Type": "application/json"}
            )
        logger.info(f"Intento de login para el usuario: {username}")
        
        # Buscar usuario por nombre de usuario
        try:
            user = db.query(User).filter(User.username == username).first()
            logger.info(f"Resultado de búsqueda de usuario: {'Encontrado' if user else 'No encontrado'}")
        except Exception as db_error:
            logger.error(f"Error al consultar la base de datos: {str(db_error)}")
            raise CommonErrors.database_error(f"Error al buscar el usuario: {str(db_error)}")
        
        # Si no existe el usuario o la contraseña es incorrecta
        if not user:
            logger.warning(f"Usuario no encontrado: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"Usuario encontrado: {user.username}")
        # Verificar contraseña
        try:
            password_valid = verify_password(password, user.password_hash)
            logger.info(f"Verificación de contraseña: {'Válida' if password_valid else 'Inválida'}")
        except Exception as pwd_error:
            logger.error(f"Error al verificar la contraseña: {str(pwd_error)}")
            raise CommonErrors.internal_error(f"Error al verificar la contraseña: {str(pwd_error)}")
            
        if not password_valid:
            logger.warning(f"Contraseña incorrecta para el usuario: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"Contraseña verificada correctamente para el usuario: {username}")
        
        # Obtener roles del usuario
        try:
            user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
            role_ids = [user_role.role_id for user_role in user_roles]
            logger.info(f"Roles del usuario {username}: {role_ids}")
        except Exception as role_error:
            logger.error(f"Error al obtener roles del usuario: {str(role_error)}")
            raise CommonErrors.database_error(f"Error al obtener roles: {str(role_error)}")
        
        # Crear datos para el token
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "roles": role_ids
        }
        
        # Generar token con duración de 12 semanas
        try:
            access_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(weeks=12)
            )
            logger.info(f"Token JWT generado correctamente para el usuario: {username}")
        except Exception as token_error:
            logger.error(f"Error al generar el token JWT: {str(token_error)}")
            raise CommonErrors.internal_error(f"Error al generar el token: {str(token_error)}")
        
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
        logger.exception("Detalles del error:")
        raise CommonErrors.internal_error(f"Error durante la autenticación: {str(e)}")
