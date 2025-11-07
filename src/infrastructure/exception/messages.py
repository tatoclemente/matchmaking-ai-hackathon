"""
Mensajes centralizados de la aplicación.

Todos los mensajes de error, éxito, info, etc. están aquí
para facilitar i18n y mantenimiento.
"""

from typing import Dict


# ============================================================================
# ERROR MESSAGES
# ============================================================================

class ErrorMessages:
    """Mensajes de error"""
    
    # Validación
    VALIDATION_ERROR = "Error de validación en los datos proporcionados"
    INVALID_INPUT = "El input proporcionado es inválido"
    MISSING_FIELD = "Campo requerido faltante: {field}"
    INVALID_RANGE = "{field} debe estar entre {min} y {max}"
    EMPTY_TEXT = "El texto no puede estar vacío"
    INVALID_UUID = "UUID inválido: {value}"
    
    # Not Found
    RESOURCE_NOT_FOUND = "{resource_type} no encontrado"
    PLAYER_NOT_FOUND = "Jugador no encontrado con ID: {player_id}"
    MATCH_NOT_FOUND = "Partido no encontrado con ID: {match_id}"
    NO_CANDIDATES_FOUND = "No se encontraron candidatos compatibles para este partido"
    
    # OpenAI
    OPENAI_ERROR = "Error comunicándose con OpenAI: {error}"
    OPENAI_RATE_LIMIT = "Se excedió el límite de requests de OpenAI. Intenta más tarde"
    OPENAI_TIMEOUT = "Timeout en llamada a OpenAI. Intenta nuevamente"
    OPENAI_INVALID_KEY = "API Key de OpenAI inválida"
    OPENAI_QUOTA_EXCEEDED = "Cuota de OpenAI excedida"
    
    # Pinecone
    PINECONE_ERROR = "Error comunicándose con Pinecone: {error}"
    PINECONE_INDEX_NOT_FOUND = "Índice de Pinecone no encontrado: {index_name}"
    PINECONE_CONNECTION_ERROR = "No se pudo conectar a Pinecone"
    
    # Database
    DATABASE_ERROR = "Error en base de datos: {error}"
    DATABASE_CONNECTION_ERROR = "No se pudo conectar a la base de datos"
    DATABASE_QUERY_ERROR = "Error ejecutando query: {query}"
    DATABASE_INTEGRITY_ERROR = "Error de integridad en base de datos"
    
    # Business Logic
    INSUFFICIENT_PLAYERS = "Se requieren {required} jugadores, solo hay {available} disponibles"
    PLAYER_ALREADY_INDEXED = "El jugador ya está indexado en el sistema"
    INVALID_ELO_RANGE = "Rango de ELO inválido: min debe ser menor que max"
    INVALID_AGE_RANGE = "Rango de edad inválido: min debe ser menor que max"
    INVALID_TIME_RANGE = "Rango horario inválido"
    BATCH_SIZE_EXCEEDED = "Tamaño de batch excedido. Máximo: {max_size}"
    
    # Authentication/Authorization
    NOT_AUTHENTICATED = "No autenticado. Proporciona credenciales válidas"
    NOT_AUTHORIZED = "No tienes permisos para realizar esta acción"
    INVALID_API_KEY = "API Key inválida o expirada"
    INVALID_CREDENTIALS = "Credenciales inválidas"
    
    # Configuration
    MISSING_CONFIG = "Configuración faltante: {config_key}"
    INVALID_CONFIG = "Configuración inválida: {config_key}"
    
    # Service
    SERVICE_UNAVAILABLE = "Servicio temporalmente no disponible: {service_name}"
    SERVICE_NOT_IMPLEMENTED = "Servicio aún no implementado: {service_name}"
    INTERNAL_ERROR = "Error interno del servidor"


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

class SuccessMessages:
    """Mensajes de éxito"""
    
    # Player
    PLAYER_INDEXED = "Jugador indexado exitosamente"
    PLAYER_UPDATED = "Jugador actualizado exitosamente"
    PLAYER_DELETED = "Jugador eliminado exitosamente"
    
    # Match
    CANDIDATES_FOUND = "Se encontraron {count} candidatos compatibles"
    MATCH_CREATED = "Partido creado exitosamente"
    MATCH_UPDATED = "Partido actualizado exitosamente"
    
    # Seeding
    PLAYERS_SEEDED = "{count} jugadores generados exitosamente"
    DATABASE_SEEDED = "Base de datos poblada exitosamente"
    
    # General
    OPERATION_SUCCESS = "Operación completada exitosamente"
    DATA_SAVED = "Datos guardados exitosamente"


# ============================================================================
# INFO MESSAGES
# ============================================================================

class InfoMessages:
    """Mensajes informativos"""
    
    # System
    SERVICE_READY = "Servicio listo y operativo"
    SERVICE_STARTING = "Iniciando servicio..."
    SERVICE_STOPPING = "Deteniendo servicio..."
    
    # Processing
    PROCESSING_REQUEST = "Procesando request..."
    SEARCHING_CANDIDATES = "Buscando candidatos compatibles..."
    GENERATING_EMBEDDINGS = "Generando embeddings..."
    CALCULATING_SCORES = "Calculando scores de compatibilidad..."
    
    # Batch
    BATCH_PROCESSING = "Procesando batch de {count} elementos..."
    BATCH_COMPLETED = "Batch procesado: {success} éxitos, {errors} errores"


# ============================================================================
# WARNING MESSAGES
# ============================================================================

class WarningMessages:
    """Mensajes de advertencia"""
    
    # Performance
    SLOW_QUERY = "Query lento detectado: {duration}ms"
    HIGH_LATENCY = "Alta latencia detectada en {service}: {latency}ms"
    
    # Limits
    APPROACHING_RATE_LIMIT = "Acercándose al límite de rate: {percentage}%"
    LOW_QUOTA = "Cuota baja en {service}: {remaining} requests restantes"
    
    # Data
    PARTIAL_RESULTS = "Resultados parciales debido a: {reason}"
    DEPRECATED_ENDPOINT = "Este endpoint está deprecado. Usa {new_endpoint} en su lugar"


# ============================================================================
# VALIDATION MESSAGES
# ============================================================================

class ValidationMessages:
    """Mensajes de validación específicos"""
    
    # ELO
    ELO_OUT_OF_RANGE = "ELO debe estar entre 800 y 3300"
    INVALID_ELO_RANGE = "ELO mínimo debe ser menor que ELO máximo"
    
    # Age
    AGE_OUT_OF_RANGE = "Edad debe estar entre 18 y 60 años"
    INVALID_AGE_RANGE = "Edad mínima debe ser menor que edad máxima"
    
    # Gender
    INVALID_GENDER = "Género debe ser MALE, FEMALE o MIXED"
    
    # Category
    INVALID_CATEGORY = "Categoría inválida: {category}"
    
    # Position
    INVALID_POSITION = "Posición inválida: {position}"
    
    # Location
    INVALID_COORDINATES = "Coordenadas inválidas: lat debe estar entre -90 y 90, lon entre -180 y 180"
    MISSING_ZONE = "Zona es requerida en location"
    
    # Time
    INVALID_TIME_FORMAT = "Formato de hora inválido. Use HH:MM (24h)"
    INVALID_DURATION = "Duración debe estar entre 60 y 180 minutos"
    
    # Players
    INVALID_PLAYER_COUNT = "Número de jugadores debe estar entre 1 y 3"
    
    # Batch
    EMPTY_BATCH = "Batch no puede estar vacío"
    BATCH_TOO_LARGE = "Batch demasiado grande. Máximo: {max_size}"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_message(template: str, **kwargs) -> str:
    """
    Formatear mensaje con variables.
    
    Args:
        template: Template del mensaje con placeholders
        **kwargs: Variables para reemplazar en el template
    
    Returns:
        Mensaje formateado
    
    Example:
        >>> format_message(ErrorMessages.PLAYER_NOT_FOUND, player_id="123")
        "Jugador no encontrado con ID: 123"
    """
    return template.format(**kwargs)


def get_error_details(error_code: str) -> Dict[str, str]:
    """
    Obtener detalles de un código de error.
    
    Args:
        error_code: Código del error
    
    Returns:
        Dict con message, description, suggested_action
    """
    error_catalog = {
        "VALIDATION_ERROR": {
            "message": ErrorMessages.VALIDATION_ERROR,
            "description": "Los datos proporcionados no cumplen con las validaciones requeridas",
            "suggested_action": "Revisa los campos marcados como inválidos y corrígelos"
        },
        "NOT_FOUND": {
            "message": ErrorMessages.RESOURCE_NOT_FOUND,
            "description": "El recurso solicitado no existe en el sistema",
            "suggested_action": "Verifica que el ID sea correcto"
        },
        "RATE_LIMIT_EXCEEDED": {
            "message": ErrorMessages.OPENAI_RATE_LIMIT,
            "description": "Se excedió el límite de requests permitidos",
            "suggested_action": "Espera unos minutos antes de reintentar"
        },
        "INTERNAL_ERROR": {
            "message": ErrorMessages.INTERNAL_ERROR,
            "description": "Ocurrió un error interno inesperado",
            "suggested_action": "Contacta al equipo de soporte si el error persiste"
        }
    }
    
    return error_catalog.get(
        error_code,
        {
            "message": "Error desconocido",
            "description": "Ocurrió un error no catalogado",
            "suggested_action": "Contacta al equipo de soporte"
        }
    )

