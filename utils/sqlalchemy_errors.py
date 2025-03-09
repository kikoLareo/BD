from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError, DataError
from utils.error_handling import APIError, ErrorCodes
from logging_config import logger
import re

def parse_integrity_error(error: IntegrityError) -> tuple[str, str]:
    """
    Analiza un error de integridad de SQLAlchemy para extraer información más específica.
    
    Args:
        error: El error de integridad de SQLAlchemy
        
    Returns:
        Una tupla con (código de error, mensaje detallado)
    """
    error_str = str(error)
    
    # Errores de clave única (UNIQUE constraint)
    if "UNIQUE constraint failed" in error_str:
        match = re.search(r"UNIQUE constraint failed: ([^\s]+)", error_str)
        if match:
            column = match.group(1).split('.')[-1]
            return ErrorCodes.DUPLICATE_ENTRY, f"Ya existe un registro con el mismo valor para '{column}'"
    
    # Errores de clave foránea (FOREIGN KEY constraint)
    if "FOREIGN KEY constraint failed" in error_str:
        return ErrorCodes.INTEGRITY_ERROR, "La operación hace referencia a un registro que no existe o está intentando eliminar un registro que está siendo utilizado por otros"
    
    # Errores de NOT NULL constraint
    if "NOT NULL constraint failed" in error_str:
        match = re.search(r"NOT NULL constraint failed: ([^\s]+)", error_str)
        if match:
            column = match.group(1).split('.')[-1]
            return ErrorCodes.MISSING_FIELDS, f"El campo '{column}' es obligatorio"
    
    # Errores de CHECK constraint
    if "CHECK constraint failed" in error_str:
        match = re.search(r"CHECK constraint failed: ([^\s]+)", error_str)
        if match:
            constraint = match.group(1)
            return ErrorCodes.VALIDATION_ERROR, f"Validación fallida para la restricción '{constraint}'"
    
    # Si no se puede identificar el error específico
    return ErrorCodes.INTEGRITY_ERROR, "Error de integridad en la base de datos"

def handle_sqlalchemy_error(error: SQLAlchemyError, entity_name: str = "recurso") -> APIError:
    """
    Maneja errores de SQLAlchemy y los convierte en APIError con mensajes más amigables.
    
    Args:
        error: El error de SQLAlchemy
        entity_name: Nombre de la entidad afectada (para mensajes más específicos)
        
    Returns:
        Un objeto APIError con información detallada
    """
    logger.error(f"Error de SQLAlchemy: {str(error)}")
    
    # Manejar errores de integridad (claves únicas, foráneas, etc.)
    if isinstance(error, IntegrityError):
        error_code, error_detail = parse_integrity_error(error)
        return APIError(
            code=error_code,
            message=f"No se pudo procesar la operación para {entity_name}",
            status_code=400,
            details=error_detail
        )
    
    # Manejar errores operacionales (conexión, timeout, etc.)
    if isinstance(error, OperationalError):
        return APIError(
            code=ErrorCodes.CONNECTION_ERROR,
            message="Error de conexión con la base de datos",
            status_code=500,
            details="No se pudo completar la operación debido a un problema de conexión con la base de datos"
        )
    
    # Manejar errores de datos (tipos incorrectos, valores fuera de rango, etc.)
    if isinstance(error, DataError):
        return APIError(
            code=ErrorCodes.INVALID_FORMAT,
            message="Datos inválidos",
            status_code=400,
            details="Los datos proporcionados no tienen el formato correcto o están fuera de rango"
        )
    
    # Manejar otros errores de SQLAlchemy
    return APIError(
        code=ErrorCodes.DATABASE_ERROR,
        message="Error en la base de datos",
        status_code=500,
        details=f"Ocurrió un error al procesar la operación en la base de datos: {str(error)}"
    )

def get_specific_error_message(error: SQLAlchemyError) -> str:
    """
    Extrae un mensaje de error más específico de un error de SQLAlchemy.
    
    Args:
        error: El error de SQLAlchemy
        
    Returns:
        Un mensaje de error más específico
    """
    error_str = str(error)
    
    # Intentar extraer mensajes específicos según el tipo de error
    if isinstance(error, IntegrityError):
        # Errores de clave única
        if "UNIQUE constraint failed" in error_str:
            match = re.search(r"UNIQUE constraint failed: ([^\s]+)", error_str)
            if match:
                column = match.group(1).split('.')[-1]
                return f"Ya existe un registro con el mismo valor para '{column}'"
        
        # Errores de clave foránea
        if "FOREIGN KEY constraint failed" in error_str:
            return "La operación hace referencia a un registro que no existe o está intentando eliminar un registro que está siendo utilizado por otros"
    
    # Si no se puede extraer un mensaje específico, devolver un mensaje genérico
    return "Error en la base de datos"
