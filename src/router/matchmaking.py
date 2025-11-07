"""
Router de Matchmaking - Endpoints principales de la API.

Define los endpoints para:
- Buscar candidatos para un partido
- Indexar jugadores
- Health checks
- Seeding de datos
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

###############################################################################
# MODELOS Pydantic (faltantes)
###############################################################################

class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado del servicio")
    service: str = Field(..., description="Nombre del servicio")
    version: str = Field(..., description="Versión")

    model_config = {
        "json_schema_extra": {
            "example": {"status": "healthy", "service": "matchmaking-ai", "version": "1.0.0"}
        }
    }


class Player(BaseModel):
    id: str = Field(..., description="ID del jugador")
    name: str = Field(..., description="Nombre")
    elo: int = Field(..., ge=0, description="ELO del jugador")
    age: Optional[int] = Field(default=None, ge=10, le=90, description="Edad")
    handedness: Optional[str] = Field(default=None, description="Mano dominante")
    description: Optional[str] = Field(default=None, description="Descripción libre")
    skills: List[str] = Field(default_factory=list, description="Habilidades")
    interests: List[str] = Field(default_factory=list, description="Intereses")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "player_123",
                "name": "Carlos",
                "elo": 1520,
                "age": 28,
                "handedness": "left",
                "skills": ["smash", "bandeja"],
                "interests": ["torneos", "competitivo"]
            }
        }
    }


class MatchRequest(BaseModel):
    match_id: str = Field(..., description="ID del match")
    required_players: int = Field(..., ge=1, le=4, description="Jugadores requeridos")
    min_elo: Optional[int] = Field(default=1000, ge=0, description="ELO mínimo")
    max_elo: Optional[int] = Field(default=2000, ge=0, description="ELO máximo")
    zone: Optional[str] = Field(default=None, description="Zona / locación")
    latitude: Optional[float] = Field(default=-31.4201, description="Latitud")
    longitude: Optional[float] = Field(default=-64.1888, description="Longitud")
    preferred_skills: List[str] = Field(default_factory=list, description="Habilidades preferidas")
    time_slot: Optional[str] = Field(default="18:00", description="Horario HH:MM")
    duration: Optional[int] = Field(default=90, description="Duración en minutos")
    categories: List[str] = Field(default_factory=list, description="Categorías aceptadas")
    gender_preference: Optional[str] = Field(default="MIXED", description="Preferencia de género")
    preferred_position: Optional[str] = Field(default=None, description="Posición preferida FOREHAND/BACKHAND")

    model_config = {
        "json_schema_extra": {
            "example": {
                "match_id": "match_789",
                "required_players": 2,
                "min_elo": 1400,
                "max_elo": 1800,
                "zone": "Nueva Córdoba",
                "latitude": -31.4201,
                "longitude": -64.1888,
                "preferred_skills": ["smash", "defense"],
                "time_slot": "19:00",
                "duration": 90,
                "categories": ["SEVENTH", "SIXTH"],
                "gender_preference": "MIXED",
                "preferred_position": "FOREHAND"
            }
        }
    }


class Candidate(BaseModel):
    player_id: str = Field(..., description="ID del jugador")
    score: float = Field(..., ge=0, le=1, description="Score normalizado [0,1]")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata adicional")

    model_config = {
        "json_schema_extra": {
            "example": {
                "player_id": "player_123",
                "score": 0.87,
                "metadata": {"elo": 1520, "skills": ["smash"]}
            }
        }
    }


class MatchmakingResponse(BaseModel):
    match_id: str
    candidates: List[Candidate]
    total_found: int
    ready_for_invitations: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "match_id": "match_789",
                "candidates": [
                    {"player_id": "player_123", "score": 0.91, "metadata": {"elo": 1520}}
                ],
                "total_found": 1,
                "ready_for_invitations": True
            }
        }
    }


class IndexPlayerResponse(BaseModel):
    message: str = Field(..., description="Mensaje de confirmación")
    player_id: str = Field(..., description="ID del jugador indexado")

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Player indexed successfully", "player_id": "player_123"}
        }
    }


class StatsResponse(BaseModel):
    total_players: int = Field(..., description="Total jugadores registrados")
    avg_elo: float = Field(..., description="Promedio ELO")
    indexed_vectors: int = Field(..., description="Vectores en índice Pinecone")
    pinecone_index: Optional[str] = Field(default=None, description="Nombre del índice")
    timestamp: str = Field(..., description="Timestamp de generación ISO8601")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_players": 1200,
                "avg_elo": 1450.5,
                "indexed_vectors": 1180,
                "pinecone_index": "matchmaking-players",
                "timestamp": "2025-11-07T10:30:00Z"
            }
        }
    }

router = APIRouter(
    prefix="/api/matchmaking",
    tags=["matchmaking"]
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verificar el estado del servicio de matchmaking"
)
async def health_check():
    """
    Health check del servicio.
    
    Returns:
        HealthResponse con status del servicio
    """
    # TODO: Aquí llamar al service para verificar conexiones
    # health_service.check_all_connections()
    
    return HealthResponse(
        status="healthy",
        service="matchmaking-ai",
        version="1.0.0"
    )


@router.post(
    "/find_candidates",
    response_model=MatchmakingResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar Candidatos",
    description="Encuentra los mejores candidatos para un partido usando IA"
)
async def find_candidates(request: MatchRequest):
    """
    Endpoint principal: encontrar candidatos para un partido.
    
    Pipeline:
    1. Crear embedding del request
    2. Buscar similares en Pinecone (top 50)
    3. Calcular scoring final
    4. Ordenar y retornar top 20
    
    Args:
        request: MatchRequest con requisitos del partido
    
    Returns:
        MatchmakingResponse con lista de candidatos ordenados por score
    
    Raises:
        HTTPException 404: No se encontraron candidatos
        HTTPException 500: Error en el proceso de matchmaking
    """
    try:
        from src.services.matchmaking_service import MatchmakingService
        from src.services.scoring_service import ScoringService
        from src.infrastructure.services.openai_service import OpenAIService
        from src.infrastructure.services.pinecone_service import PineconeService
        from src.infrastructure.external.openai_client import openai_client, init_openai_client
        from src.infrastructure.external.pinecone_client import pinecone_client, init_pinecone_client
        from src.infrastructure.schema.embedding import ClientConfig
        from src.infrastructure.config import config as infra_config
        from src.services.request_adapter import adapt_router_request_to_scoring
        
        # Asegurar que los clientes estén inicializados
        if openai_client is None:
            openai_config = ClientConfig(api_key=infra_config.OPENAI_API_KEY)
            init_openai_client(openai_config)
        
        if pinecone_client is None:
            init_pinecone_client()
        
        # Inicializar servicios
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        scoring_service = ScoringService()
        matchmaking_service = MatchmakingService(openai_service, pinecone_service, scoring_service)
        
        # Adaptar request al formato de scoring
        request_dict = request.model_dump()
        adapted_request = adapt_router_request_to_scoring(request_dict)
        
        # Buscar candidatos
        candidates_data = await matchmaking_service.find_candidates(adapted_request)
        
        if not candidates_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron candidatos para este partido"
            )
        
        # Convertir a formato de respuesta
        candidates = [
            Candidate(
                player_id=c['player_id'],
                score=c['score'],
                metadata={
                    'distance_km': c['distance_km'],
                    'reasons': c['reasons'],
                    **c.get('metadata', {})
                }
            )
            for c in candidates_data
        ]
        
        return MatchmakingResponse(
            match_id=request.match_id,
            candidates=candidates,
            total_found=len(candidates),
            ready_for_invitations=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en matchmaking: {str(e)}"
        )


@router.post(
    "/index_player",
    response_model=IndexPlayerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Indexar Jugador",
    description="Indexa un jugador en el sistema de embeddings vectoriales"
)
async def index_player(player: Player):
    """
    Indexar un jugador en Pinecone.
    
    Proceso:
    1. Crear embedding del jugador
    2. Guardar en Pinecone con metadata
    3. Actualizar métricas en DB
    
    Args:
        player: Objeto Player con datos del jugador
    
    Returns:
        IndexPlayerResponse confirmando la indexación
    
    Raises:
        HTTPException 500: Error al indexar
    """
    try:
        # TODO: Aquí llamar al IndexingService
        # indexing_service = get_indexing_service()
        # await indexing_service.index_player(player)
        
        # return IndexPlayerResponse(
        #     message="Player indexed successfully",
        #     player_id=player.id
        # )
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="IndexingService aún no implementado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexando jugador: {str(e)}"
        )


@router.delete(
    "/players/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Jugador",
    description="Elimina un jugador del índice de Pinecone"
)
async def delete_player(player_id: str):
    """
    Eliminar un jugador del sistema.
    
    Args:
        player_id: UUID del jugador a eliminar
    
    Raises:
        HTTPException 404: Jugador no encontrado
        HTTPException 500: Error al eliminar
    """
    try:
        # TODO: Aquí llamar al IndexingService
        # indexing_service = get_indexing_service()
        # await indexing_service.delete_player(player_id)
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Delete aún no implementado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando jugador: {str(e)}"
        )


@router.get(
    "/players/{player_id}",
    response_model=Player,
    summary="Obtener Jugador",
    description="Obtiene información de un jugador por ID"
)
async def get_player(player_id: str):
    """
    Obtener datos de un jugador.
    
    Args:
        player_id: UUID del jugador
    
    Returns:
        Player con todos los datos
    
    Raises:
        HTTPException 404: Jugador no encontrado
    """
    try:
        # TODO: Aquí llamar al PlayerService
        # player_service = get_player_service()
        # player = await player_service.get_by_id(player_id)
        
        # if not player:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Jugador {player_id} no encontrado"
        #     )
        
        # return player
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PlayerService aún no implementado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo jugador: {str(e)}"
        )


@router.get(
    "/stats",
    summary="Estadísticas del Sistema",
    description="Obtiene estadísticas generales del sistema de matchmaking"
)
async def get_stats():
    """
    Obtener estadísticas del sistema.
    
    Returns:
        Dict con estadísticas: total_players, avg_elo, etc.
    """
    try:
        # TODO: Aquí llamar al StatsService
        # stats_service = get_stats_service()
        # stats = await stats_service.get_system_stats()
        
        # return stats
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="StatsService aún no implementado"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo stats: {str(e)}"
        )

