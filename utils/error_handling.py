from fastapi import HTTPException, status
from typing import Dict, Any, Optional, Union, List
from logging_config import logger

# Definición de códigos de error personalizados
class ErrorCodes:
    # Errores de autenticación
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # Errores de autorización
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INSUFFICIENT_PRIVILEGES = "INSUFFICIENT_PRIVILEGES"
    
    # Errores de validación
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"
    MISSING_FIELDS = "MISSING_FIELDS"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    
    # Errores de recursos
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    
    # Errores de base de datos
    DATABASE_ERROR = "DATABASE_ERROR"
    INTEGRITY_ERROR = "INTEGRITY_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    
    # Errores generales
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    OPERATION_FAILED = "OPERATION_FAILED"

# Clase para errores de la API
class APIError(Exception):
    def __init__(
        self, 
        code: str, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Union[str, Dict[str, Any], List[Dict[str, Any]]]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

# Función para convertir APIError a HTTPException
def api_error_to_http_exception(error: APIError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={
            "code": error.code,
            "message": error.message,
            "details": error.details
        }
    )

# Errores comunes predefinidos
class CommonErrors:
    @staticmethod
    def not_found(resource_type: str, resource_id: Any) -> APIError:
        return APIError(
            code=ErrorCodes.NOT_FOUND,
            message=f"{resource_type} no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
            details=f"No se encontró {resource_type.lower()} con ID {resource_id}"
        )
    
    @staticmethod
    def already_exists(resource_type: str, identifier: str) -> APIError:
        return APIError(
            code=ErrorCodes.ALREADY_EXISTS,
            message=f"{resource_type} ya existe",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=f"Ya existe un {resource_type.lower()} con {identifier}"
        )
    
    @staticmethod
    def invalid_credentials() -> APIError:
        return APIError(
            code=ErrorCodes.INVALID_CREDENTIALS,
            message="Credenciales inválidas",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="El nombre de usuario o la contraseña son incorrectos"
        )
    
    @staticmethod
    def permission_denied() -> APIError:
        return APIError(
            code=ErrorCodes.PERMISSION_DENIED,
            message="Permiso denegado",
            status_code=status.HTTP_403_FORBIDDEN,
            details="No tienes permisos para realizar esta acción"
        )
    
    @staticmethod
    def validation_error(details: Union[str, Dict[str, Any], List[Dict[str, Any]]]) -> APIError:
        return APIError(
            code=ErrorCodes.VALIDATION_ERROR,
            message="Error de validación",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )
    
    @staticmethod
    def database_error(details: str) -> APIError:
        return APIError(
            code=ErrorCodes.DATABASE_ERROR,
            message="Error en la base de datos",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
    
    @staticmethod
    def internal_error(details: Optional[str] = None) -> APIError:
        return APIError(
            code=ErrorCodes.INTERNAL_ERROR,
            message="Error interno del servidor",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details or "Ha ocurrido un error inesperado"
        )

# Decorador para manejar excepciones en endpoints
def handle_exceptions(func):
    import inspect
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Verificar si la función es asíncrona o no
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except APIError as e:
            logger.error(f"APIError: {e.code} - {e.message}", extra={"details": e.details})
            raise api_error_to_http_exception(e)
        except HTTPException as e:
            logger.error(f"HTTPException: {e.status_code} - {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            error = CommonErrors.internal_error(str(e))
            raise api_error_to_http_exception(error)
    
    # Si la función original no es asíncrona, devolver una versión no asíncrona del wrapper
    if not inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                logger.error(f"APIError: {e.code} - {e.message}", extra={"details": e.details})
                raise api_error_to_http_exception(e)
            except HTTPException as e:
                logger.error(f"HTTPException: {e.status_code} - {e.detail}")
                raise e
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                error = CommonErrors.internal_error(str(e))
                raise api_error_to_http_exception(error)
        return sync_wrapper
    
    return wrapper
