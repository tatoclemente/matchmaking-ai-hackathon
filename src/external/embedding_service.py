"""
Servicio de alto nivel para embeddings.

Este servicio orquesta la creación de embeddings para jugadores y match requests,
usando el proveedor configurado (OpenAI, Anthropic, etc.) a través del patrón Adapter.
"""

from typing import List, Optional
import logging

from src.models.player import Player
from src.models.match_request import MatchRequest
from .embedding_provider import EmbeddingProvider

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Servicio de alto nivel para crear embeddings de jugadores y match requests.
    
    Este servicio:
    - Construye textos descriptivos ricos
    - Delega la generación de embeddings al provider
    - Maneja la lógica de negocio específica del dominio
    """

    def __init__(self, provider: EmbeddingProvider):
        """
        Inicializar el servicio con un proveedor de embeddings.

        Args:
            provider: Implementación de EmbeddingProvider (OpenAI, Anthropic, etc.)
        """
        self.provider = provider
        logger.info(f"✅ EmbeddingService initialized with provider: {provider.get_provider_name()}")

    def create_player_embedding(self, player: Player) -> List[float]:
        """
        Crear embedding del perfil de un jugador.

        Args:
            player: Objeto Player con todos sus datos

        Returns:
            Vector de embeddings

        Raises:
            EmbeddingError: Si falla la generación
        """
        description = self._build_player_description(player)
        logger.debug(f"🎯 Creating embedding for player {player.id}: {description[:100]}...")
        
        return self.provider.create_embedding(description)

    def create_request_embedding(self, request: MatchRequest) -> List[float]:
        """
        Crear embedding de los requisitos de un partido.

        Args:
            request: Objeto MatchRequest con requisitos del partido

        Returns:
            Vector de embeddings

        Raises:
            EmbeddingError: Si falla la generación
        """
        description = self._build_request_description(request)
        logger.debug(f"🎯 Creating embedding for match {request.match_id}: {description[:100]}...")
        
        return self.provider.create_embedding(description)

    def create_players_embeddings_batch(self, players: List[Player]) -> List[List[float]]:
        """
        Crear embeddings para múltiples jugadores en batch.

        Args:
            players: Lista de jugadores (máximo 100)

        Returns:
            Lista de vectores de embeddings

        Raises:
            EmbeddingError: Si falla la generación
        """
        descriptions = [self._build_player_description(p) for p in players]
        logger.info(f"📦 Creating embeddings for {len(players)} players in batch...")
        
        return self.provider.create_embeddings_batch(descriptions)

    def _build_player_description(self, player: Player) -> str:
        """
        Construir descripción rica del jugador para el embedding.

        Esta descripción captura:
        - Perfil técnico (categoría, ELO, posiciones)
        - Perfil personal (edad, género)
        - Ubicación geográfica
        - Disponibilidad horaria
        - Comportamiento (acceptance_rate, actividad)

        Args:
            player: Objeto Player

        Returns:
            Texto descriptivo rico
        """
        parts = [
            f"Jugador de pádel categoría {player.category}",
            f"ELO {player.elo}",
            f"Edad {player.age} años",
            f"Género {player.gender}",
            f"Juega de {' y '.join(player.positions)}",
            f"Zona {player.location['zone']}"
        ]

        # Agregar disponibilidad si existe
        if player.availability and len(player.availability) > 0:
            time_ranges = [
                f"{slot['min']}-{slot['max']}" 
                for slot in player.availability
            ]
            parts.append(f"Disponible {', '.join(time_ranges)}")

        # Agregar contexto comportamental
        if player.acceptance_rate > 0.8:
            parts.append("Jugador muy confiable y activo")
        elif player.acceptance_rate > 0.6:
            parts.append("Jugador confiable")
        elif player.acceptance_rate < 0.4:
            parts.append("Jugador ocasional")

        if player.last_active_days < 3:
            parts.append("Usuario muy activo recientemente")
        elif player.last_active_days < 7:
            parts.append("Usuario activo")

        # Unir todo en una oración coherente
        return ". ".join(parts) + "."

    def _build_request_description(self, request: MatchRequest) -> str:
        """
        Construir descripción de los requisitos del partido.

        Esta descripción captura:
        - Categorías y nivel (ELO) aceptado
        - Preferencias demográficas (género, edad)
        - Ubicación del partido
        - Horario y duración
        - Posición preferida (si se especifica)

        Args:
            request: Objeto MatchRequest

        Returns:
            Texto descriptivo de los requisitos
        """
        parts = [
            f"Partido de pádel categorías {', '.join(request.categories)}",
            f"ELO entre {request.elo_range[0]} y {request.elo_range[1]}",
            f"Zona {request.location['zone']}",
            f"Horario {request.match_time}",
            f"Duración {request.required_time} minutos",
            f"Género {request.gender_preference}"
        ]

        # Agregar rango de edad si está especificado
        if request.age_range:
            parts.append(
                f"Edad entre {request.age_range[0]} y {request.age_range[1]} años"
            )

        # Agregar posición preferida si está especificada
        if request.preferred_position:
            parts.append(f"Se busca jugador de {request.preferred_position.lower()}")

        # Agregar contexto sobre número de jugadores
        parts.append(f"Se necesitan {request.required_players} jugadores")

        return ". ".join(parts) + "."

    def get_embedding_dimension(self) -> int:
        """
        Obtener la dimensión de los embeddings del proveedor actual.

        Returns:
            Dimensión del vector de embeddings
        """
        return self.provider.get_embedding_dimension()

    def get_provider_name(self) -> str:
        """
        Obtener el nombre del proveedor actual.

        Returns:
            Nombre del proveedor (e.g., "OpenAI")
        """
        return self.provider.get_provider_name()

    def validate_health(self) -> bool:
        """
        Verificar que el servicio está funcionando correctamente.

        Returns:
            True si el proveedor está operativo
        """
        return self.provider.validate_health()

