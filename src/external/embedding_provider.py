"""
Protocolo abstracto para proveedores de embeddings.

Este módulo define la interfaz que deben implementar todos los
proveedores de embeddings (OpenAI, Anthropic, Cohere, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Protocol


class EmbeddingProvider(ABC):
    """
    Interfaz abstracta para proveedores de embeddings.
    
    Cualquier proveedor (OpenAI, Anthropic, Cohere) debe implementar
    estos métodos para ser compatible con el sistema.
    """

    @abstractmethod
    def create_embedding(self, text: str) -> List[float]:
        """
        Crear embedding para un texto individual.

        Args:
            text: Texto a convertir en embedding

        Returns:
            Vector de embeddings (dimensiones dependen del modelo)

        Raises:
            EmbeddingError: Si falla la generación del embedding
        """
        pass

    @abstractmethod
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Crear embeddings en batch para múltiples textos.

        Args:
            texts: Lista de textos a convertir

        Returns:
            Lista de vectores de embeddings

        Raises:
            EmbeddingError: Si falla la generación
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Obtener la dimensión de los embeddings de este proveedor.

        Returns:
            Número de dimensiones (e.g., 1536 para OpenAI text-embedding-3-small)
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Obtener el nombre del proveedor.

        Returns:
            Nombre del proveedor (e.g., "OpenAI", "Anthropic")
        """
        pass

    @abstractmethod
    def validate_health(self) -> bool:
        """
        Verificar que el proveedor está disponible y funcionando.

        Returns:
            True si el proveedor está operativo
        """
        pass


class EmbeddingError(Exception):
    """Excepción base para errores de embedding"""
    pass


class ProviderUnavailableError(EmbeddingError):
    """El proveedor no está disponible o no responde"""
    pass


class InvalidInputError(EmbeddingError):
    """El input proporcionado no es válido"""
    pass


class RateLimitError(EmbeddingError):
    """Se excedió el rate limit del proveedor"""
    pass

