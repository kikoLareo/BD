from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from logging_config import logger
from utils.error_handling import ErrorCodes

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador personalizado para errores de validación de Pydantic.
    Convierte los errores de validación en respuestas JSON estructuradas.
    
    Args:
        request: La solicitud que causó el error
        exc: La excepción de validación
        
    Returns:
        Una respuesta JSON con detalles del error
    """
    errors = []
    
    for error in exc.errors():
        # Extraer información del error
        loc = error.get("loc", [])
        field = loc[-1] if loc else None
        error_type = error.get("type", "")
        msg = error.get("msg", "")
        
        # Crear un mensaje de error más amigable
        if error_type == "missing":
            friendly_msg = f"El campo '{field}' es obligatorio"
        elif error_type == "type_error":
            friendly_msg = f"El campo '{field}' tiene un tipo de dato incorrecto"
        elif error_type == "value_error":
            friendly_msg = f"El valor del campo '{field}' no es válido"
        else:
            friendly_msg = msg
        
        errors.append({
            "field": field,
            "message": friendly_msg,
            "error_type": error_type
        })
    
    # Registrar el error
    logger.warning(
        f"Error de validación en {request.method} {request.url.path}",
        extra={"validation_errors": errors}
    )
    
    # Construir la respuesta
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": ErrorCodes.VALIDATION_ERROR,
            "message": "Error de validación",
            "details": {
                "errors": errors
            }
        }
    )

def register_exception_handlers(app):
    """
    Registra los manejadores de excepciones personalizados en la aplicación.
    
    Args:
        app: La aplicación FastAPI
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
