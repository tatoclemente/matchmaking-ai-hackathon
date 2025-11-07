"""
Router de ejemplo mostrando el uso del sistema de excepciones.

Este archivo es solo para referencia y testing del sistema de excepciones.
"""

from fastapi import APIRouter, Query

from src.exceptions import (
    PlayerNotFoundError,
    ValidationError,
    OpenAIRateLimitError,
    NoCandidatesFoundError,
    InvalidEloRangeError,
    DatabaseConnectionError
)
from src.messages import ErrorMessages, SuccessMessages, format_message


router = APIRouter(
    prefix="/api/examples",
    tags=["examples"]
)


@router.get("/test-player-not-found")
async def test_player_not_found(player_id: str = Query(default="test-123")):
    """
    Endpoint de ejemplo: PlayerNotFoundError
    
    Prueba: GET /api/examples/test-player-not-found?player_id=abc-123
    """
    # Simular que no se encuentra el jugador
    raise PlayerNotFoundError(player_id=player_id)


@router.get("/test-validation-error")
async def test_validation_error(elo: int = Query(default=9999)):
    """
    Endpoint de ejemplo: ValidationError
    
    Prueba: GET /api/examples/test-validation-error?elo=9999
    """
    if elo < 800 or elo > 3300:
        raise ValidationError(
            message=format_message(
                ErrorMessages.INVALID_RANGE,
                field="elo",
                min=800,
                max=3300
            ),
            details={"field": "elo", "value": elo, "min": 800, "max": 3300}
        )
    
    return {"message": "ELO válido", "elo": elo}


@router.get("/test-rate-limit")
async def test_rate_limit():
    """
    Endpoint de ejemplo: OpenAIRateLimitError
    
    Prueba: GET /api/examples/test-rate-limit
    """
    # Simular rate limit de OpenAI
    raise OpenAIRateLimitError(retry_after=60)


@router.get("/test-no-candidates")
async def test_no_candidates(match_id: str = Query(default="match-123")):
    """
    Endpoint de ejemplo: NoCandidatesFoundError
    
    Prueba: GET /api/examples/test-no-candidates?match_id=match-456
    """
    # Simular que no se encontraron candidatos
    raise NoCandidatesFoundError(match_id=match_id)


@router.get("/test-invalid-elo-range")
async def test_invalid_elo_range(
    min_elo: int = Query(default=2000),
    max_elo: int = Query(default=1500)
):
    """
    Endpoint de ejemplo: InvalidEloRangeError
    
    Prueba: GET /api/examples/test-invalid-elo-range?min_elo=2000&max_elo=1500
    """
    if min_elo >= max_elo:
        raise InvalidEloRangeError(min_elo=min_elo, max_elo=max_elo)
    
    return {"message": "Rango válido", "range": [min_elo, max_elo]}


@router.get("/test-database-error")
async def test_database_error():
    """
    Endpoint de ejemplo: DatabaseConnectionError
    
    Prueba: GET /api/examples/test-database-error
    """
    # Simular error de conexión a base de datos
    raise DatabaseConnectionError()


@router.get("/test-unhandled-exception")
async def test_unhandled_exception():
    """
    Endpoint de ejemplo: Excepción no manejada (catch-all)
    
    Prueba: GET /api/examples/test-unhandled-exception
    
    Este endpoint genera un ValueError para mostrar cómo el handler
    catch-all captura excepciones no específicas.
    """
    # Simular una excepción no manejada
    result = 10 / 0  # ZeroDivisionError
    return {"result": result}


@router.get("/test-success")
async def test_success(count: int = Query(default=100)):
    """
    Endpoint de ejemplo: Respuesta exitosa con mensaje del catálogo
    
    Prueba: GET /api/examples/test-success?count=100
    """
    return {
        "success": True,
        "message": format_message(
            SuccessMessages.PLAYERS_SEEDED,
            count=count
        ),
        "data": {
            "count": count,
            "status": "completed"
        }
    }


@router.get("/test-all-errors")
async def test_all_errors():
    """
    Endpoint que lista todos los tipos de errores disponibles.
    
    Útil para documentación y referencia.
    """
    return {
        "available_exceptions": {
            "validation": [
                "ValidationError",
                "InvalidInputError",
                "MissingFieldError",
                "InvalidRangeError"
            ],
            "not_found": [
                "NotFoundError",
                "PlayerNotFoundError",
                "MatchNotFoundError",
                "NoCandidatesFoundError"
            ],
            "external_services": [
                "ExternalServiceError",
                "OpenAIError",
                "OpenAIRateLimitError",
                "OpenAITimeoutError",
                "PineconeError",
                "DatabaseError",
                "DatabaseConnectionError"
            ],
            "business_logic": [
                "BusinessLogicError",
                "InsufficientPlayersError",
                "PlayerAlreadyIndexedError",
                "InvalidEloRangeError"
            ],
            "auth": [
                "AuthenticationError",
                "AuthorizationError",
                "InvalidAPIKeyError"
            ],
            "internal": [
                "InternalError",
                "ConfigurationError",
                "ServiceNotAvailableError"
            ]
        },
        "test_endpoints": {
            "player_not_found": "/api/examples/test-player-not-found",
            "validation_error": "/api/examples/test-validation-error?elo=9999",
            "rate_limit": "/api/examples/test-rate-limit",
            "no_candidates": "/api/examples/test-no-candidates",
            "invalid_range": "/api/examples/test-invalid-elo-range",
            "database_error": "/api/examples/test-database-error",
            "unhandled": "/api/examples/test-unhandled-exception",
            "success": "/api/examples/test-success"
        }
    }

