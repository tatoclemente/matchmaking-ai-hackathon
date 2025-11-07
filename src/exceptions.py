"""
Excepciones personalizadas de la aplicación.

Define todas las excepciones custom con jerarquía clara.
"""

from typing import Any, Dict, Optional


# ============================================================================
# BASE EXCEPTION
# ============================================================================

class AppException(Exception):
    """
    Excepción base de la aplicación.
    
    Todas las excepciones custom heredan de esta.
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# ============================================================================
# VALIDATION ERRORS (400)
# ============================================================================

class ValidationError(AppException):
    """Error de validación de datos"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class InvalidInputError(ValidationError):
    """Input inválido o malformado"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else None
        super().__init__(message=message, details=details)


class MissingFieldError(ValidationError):
    """Campo requerido faltante"""
    
    def __init__(self, field: str):
        super().__init__(
            message=f"Campo requerido faltante: {field}",
            details={"field": field}
        )


class InvalidRangeError(ValidationError):
    """Valor fuera de rango permitido"""
    
    def __init__(self, field: str, min_val: Any, max_val: Any, current_val: Any):
        super().__init__(
            message=f"{field} debe estar entre {min_val} y {max_val}, recibido: {current_val}",
            details={
                "field": field,
                "min": min_val,
                "max": max_val,
                "current": current_val
            }
        )


# ============================================================================
# NOT FOUND ERRORS (404)
# ============================================================================

class NotFoundError(AppException):
    """Recurso no encontrado"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details
        )


class PlayerNotFoundError(NotFoundError):
    """Jugador no encontrado"""
    
    def __init__(self, player_id: str):
        super().__init__(
            message=f"Jugador no encontrado",
            resource_type="Player",
            resource_id=player_id
        )


class MatchNotFoundError(NotFoundError):
    """Partido no encontrado"""
    
    def __init__(self, match_id: str):
        super().__init__(
            message=f"Partido no encontrado",
            resource_type="Match",
            resource_id=match_id
        )


class NoCandidatesFoundError(NotFoundError):
    """No se encontraron candidatos para el partido"""
    
    def __init__(self, match_id: str):
        super().__init__(
            message="No se encontraron candidatos compatibles para este partido",
            resource_type="Candidates",
            resource_id=match_id
        )


# ============================================================================
# EXTERNAL SERVICE ERRORS (502, 503)
# ============================================================================

class ExternalServiceError(AppException):
    """Error en servicio externo"""
    
    def __init__(self, service_name: str, message: str, status_code: int = 502):
        super().__init__(
            message=f"Error en servicio {service_name}: {message}",
            status_code=status_code,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service_name}
        )


class OpenAIError(ExternalServiceError):
    """Error de OpenAI API"""
    
    def __init__(self, message: str):
        super().__init__(service_name="OpenAI", message=message)


class OpenAIRateLimitError(OpenAIError):
    """Rate limit de OpenAI excedido"""
    
    def __init__(self, retry_after: Optional[int] = None):
        message = "Rate limit de OpenAI excedido"
        if retry_after:
            message += f". Reintentar en {retry_after} segundos"
        super().__init__(message=message)
        self.status_code = 429
        self.error_code = "RATE_LIMIT_EXCEEDED"
        if retry_after:
            self.details["retry_after"] = retry_after


class OpenAITimeoutError(OpenAIError):
    """Timeout en llamada a OpenAI"""
    
    def __init__(self):
        super().__init__(message="Timeout en llamada a OpenAI")
        self.status_code = 504
        self.error_code = "TIMEOUT"


class PineconeError(ExternalServiceError):
    """Error de Pinecone API"""
    
    def __init__(self, message: str):
        super().__init__(service_name="Pinecone", message=message)


class DatabaseError(ExternalServiceError):
    """Error de base de datos"""
    
    def __init__(self, message: str):
        super().__init__(service_name="Database", message=message)
        self.status_code = 503


class DatabaseConnectionError(DatabaseError):
    """Error de conexión a base de datos"""
    
    def __init__(self):
        super().__init__(message="No se pudo conectar a la base de datos")
        self.error_code = "DB_CONNECTION_ERROR"


# ============================================================================
# BUSINESS LOGIC ERRORS (409, 422)
# ============================================================================

class BusinessLogicError(AppException):
    """Error de lógica de negocio"""
    
    def __init__(self, message: str, status_code: int = 422):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code="BUSINESS_LOGIC_ERROR"
        )


class InsufficientPlayersError(BusinessLogicError):
    """No hay suficientes jugadores para el partido"""
    
    def __init__(self, required: int, available: int):
        super().__init__(
            message=f"Se requieren {required} jugadores, pero solo hay {available} disponibles",
        )
        self.details = {
            "required": required,
            "available": available
        }


class PlayerAlreadyIndexedError(BusinessLogicError):
    """Jugador ya está indexado"""
    
    def __init__(self, player_id: str):
        super().__init__(
            message=f"El jugador ya está indexado en el sistema",
        )
        self.status_code = 409
        self.error_code = "ALREADY_EXISTS"
        self.details = {"player_id": player_id}


class InvalidEloRangeError(BusinessLogicError):
    """Rango de ELO inválido"""
    
    def __init__(self, min_elo: int, max_elo: int):
        super().__init__(
            message=f"Rango de ELO inválido: min ({min_elo}) debe ser menor que max ({max_elo})",
        )
        self.details = {
            "min_elo": min_elo,
            "max_elo": max_elo
        }


# ============================================================================
# AUTHENTICATION/AUTHORIZATION ERRORS (401, 403)
# ============================================================================

class AuthenticationError(AppException):
    """Error de autenticación"""
    
    def __init__(self, message: str = "No autenticado"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(AppException):
    """Error de autorización"""
    
    def __init__(self, message: str = "No autorizado"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class InvalidAPIKeyError(AuthenticationError):
    """API Key inválida"""
    
    def __init__(self):
        super().__init__(message="API Key inválida o expirada")
        self.error_code = "INVALID_API_KEY"


# ============================================================================
# INTERNAL ERRORS (500)
# ============================================================================

class InternalError(AppException):
    """Error interno del servidor"""
    
    def __init__(self, message: str = "Error interno del servidor"):
        super().__init__(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR"
        )


class ConfigurationError(InternalError):
    """Error de configuración"""
    
    def __init__(self, config_key: str):
        super().__init__(
            message=f"Configuración faltante o inválida: {config_key}"
        )
        self.error_code = "CONFIGURATION_ERROR"
        self.details = {"config_key": config_key}


class ServiceNotAvailableError(InternalError):
    """Servicio no disponible"""
    
    def __init__(self, service_name: str):
        super().__init__(
            message=f"Servicio no disponible: {service_name}"
        )
        self.status_code = 503
        self.error_code = "SERVICE_UNAVAILABLE"
        self.details = {"service": service_name}

