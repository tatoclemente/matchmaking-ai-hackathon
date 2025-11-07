"""
Exception Handler Global para FastAPI.

Captura y maneja todas las excepciones de forma centralizada.
"""

import logging
import traceback
from typing import Union, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

try:
    # Nueva ubicación (infraestructura) esperada
    from src.infrastructure.exception.exceptions import AppException  # type: ignore
    from src.infrastructure.exception.messages import ErrorMessages, format_message  # type: ignore
except ModuleNotFoundError:
    # Fallback si la estructura cambia o en tests legacy
    from src.infrastructure.exception.exceptions import AppException  # type: ignore
    from src.infrastructure.exception.messages import ErrorMessages, format_message  # type: ignore


# Configurar logger
logger = logging.getLogger(__name__)


# ============================================================================
# RESPONSE MODELS
# ============================================================================

def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[dict] = None,
    path: Optional[str] = None
) -> dict:
    """
    Crear estructura estandarizada de respuesta de error.
    
    Args:
        error_code: Código único del error
        message: Mensaje descriptivo
        status_code: HTTP status code
        details: Detalles adicionales del error
        path: Path del request que falló
    
    Returns:
        Dict con estructura de error
    """
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "status_code": status_code
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if path:
        response["error"]["path"] = path
    
    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handler para excepciones personalizadas de la aplicación.
    
    Args:
        request: Request de FastAPI
        exc: Excepción personalizada
    
    Returns:
        JSONResponse con error formateado
    """
    logger.error(
        f"AppException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            path=request.url.path
        )
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handler para errores de validación de Pydantic.
    
    Args:
        request: Request de FastAPI
        exc: Error de validación
    
    Returns:
        JSONResponse con errores de validación formateados
    """
    # Extraer errores de validación
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error on {request.url.path}",
        extra={
            "errors": errors,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            error_code="VALIDATION_ERROR",
            message=ErrorMessages.VALIDATION_ERROR,
            status_code=422,
            details={"validation_errors": errors},
            path=request.url.path
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler para excepciones no capturadas.
    
    Args:
        request: Request de FastAPI
        exc: Excepción genérica
    
    Returns:
        JSONResponse con error interno
    """
    # Log completo del error con traceback
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # En producción, no exponer detalles internos
    # En desarrollo, incluir más información
    details = {}
    if logger.level == logging.DEBUG:
        details = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc()
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            error_code="INTERNAL_ERROR",
            message=ErrorMessages.INTERNAL_ERROR,
            status_code=500,
            details=details,
            path=request.url.path
        )
    )


# ============================================================================
# REGISTRATION
# ============================================================================

def register_exception_handlers(app: FastAPI) -> None:
    """
    Registrar todos los exception handlers en la app de FastAPI.
    
    Args:
        app: Instancia de FastAPI
    """
    # Handler para excepciones personalizadas
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    
    # Handler para errores de validación de Pydantic
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, validation_exception_handler)  # type: ignore[arg-type]
    
    # Handler catch-all para excepciones no manejadas
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("✅ Exception handlers registered successfully")

