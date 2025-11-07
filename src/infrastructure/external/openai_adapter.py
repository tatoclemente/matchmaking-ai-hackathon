"""
Adapter para OpenAI Embeddings API.

Este módulo implementa el patrón Adapter para OpenAI,
permitiendo cambiar de proveedor sin afectar el resto del sistema.
"""

from openai import OpenAI
from openai import RateLimitError as OpenAIRateLimitError
from openai import APIError, APIConnectionError
from typing import List
import logging
from threading import Lock

from .embedding_provider import (
    EmbeddingProvider,
    EmbeddingError,
    ProviderUnavailableError,
    RateLimitError,
    InvalidInputError
)

logger = logging.getLogger(__name__)


class OpenAIAdapter(EmbeddingProvider):
    """
    Adapter para OpenAI Embeddings API.
    
    Implementa la interfaz EmbeddingProvider usando el cliente de OpenAI.
    Singleton thread-safe.
    """

    _instance = None
    _lock = Lock()

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Constructor privado. Usar get_instance() en su lugar.

        Args:
            api_key: API key de OpenAI
            model: Modelo a usar (default: text-embedding-3-small)
        """
        if OpenAIAdapter._instance is not None:
            raise Exception("Usa OpenAIAdapter.get_instance() para obtener la instancia")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self._dimension = self._get_model_dimension(model)
        
        logger.info(f"✅ OpenAI Adapter initialized with model: {model}")

    @classmethod
    def get_instance(cls, api_key: str = None, model: str = "text-embedding-3-small") -> "OpenAIAdapter":
        """
        Factory method thread-safe para obtener la instancia singleton.

        Args:
            api_key: API key de OpenAI (solo necesario en primera llamada)
            model: Modelo a usar

        Returns:
            Instancia singleton de OpenAIAdapter
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if api_key is None:
                        raise ValueError("api_key es requerido en la primera inicialización")
                    cls._instance = cls(api_key, model)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Resetear la instancia singleton (útil para testing)"""
        cls._instance = None

    def create_embedding(self, text: str) -> List[float]:
        """
        Crear embedding para un texto usando OpenAI.

        Args:
            text: Texto a convertir en embedding

        Returns:
            Vector de 1536 dimensiones (para text-embedding-3-small)

        Raises:
            EmbeddingError: Si falla la generación
        """
        if not text or not text.strip():
            raise InvalidInputError("El texto no puede estar vacío")

        try:
            logger.debug(f"📊 Creating embedding for text: {text[:50]}...")
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            
            # Validar dimensiones
            if len(embedding) != self._dimension:
                raise EmbeddingError(
                    f"Dimensión inesperada: {len(embedding)} (esperado: {self._dimension})"
                )
            
            logger.debug(f"✅ Embedding created successfully ({len(embedding)} dims)")
            return embedding

        except OpenAIRateLimitError as e:
            logger.error(f"⚠️ Rate limit exceeded: {e}")
            raise RateLimitError(f"Rate limit de OpenAI excedido: {e}")

        except APIConnectionError as e:
            logger.error(f"❌ Connection error: {e}")
            raise ProviderUnavailableError(f"No se pudo conectar a OpenAI: {e}")

        except APIError as e:
            logger.error(f"❌ OpenAI API error: {e}")
            raise EmbeddingError(f"Error en OpenAI API: {e}")

        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            raise EmbeddingError(f"Error inesperado al crear embedding: {e}")

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Crear embeddings en batch (hasta 100 textos según límites de OpenAI).

        Args:
            texts: Lista de textos a convertir

        Returns:
            Lista de vectores de embeddings

        Raises:
            EmbeddingError: Si falla la generación
        """
        if not texts:
            raise InvalidInputError("La lista de textos no puede estar vacía")

        if len(texts) > 100:
            raise InvalidInputError("OpenAI permite máximo 100 textos por batch")

        try:
            logger.debug(f"📊 Creating {len(texts)} embeddings in batch...")
            
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                encoding_format="float"
            )
            
            embeddings = [item.embedding for item in response.data]
            
            # Validar que todos tienen la dimensión correcta
            for i, emb in enumerate(embeddings):
                if len(emb) != self._dimension:
                    raise EmbeddingError(
                        f"Embedding {i} tiene dimensión incorrecta: {len(emb)}"
                    )
            
            logger.debug(f"✅ {len(embeddings)} embeddings created successfully")
            return embeddings

        except OpenAIRateLimitError as e:
            logger.error(f"⚠️ Rate limit exceeded: {e}")
            raise RateLimitError(f"Rate limit de OpenAI excedido: {e}")

        except APIConnectionError as e:
            logger.error(f"❌ Connection error: {e}")
            raise ProviderUnavailableError(f"No se pudo conectar a OpenAI: {e}")

        except APIError as e:
            logger.error(f"❌ OpenAI API error: {e}")
            raise EmbeddingError(f"Error en OpenAI API: {e}")

        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            raise EmbeddingError(f"Error inesperado en batch: {e}")

    def get_embedding_dimension(self) -> int:
        """
        Obtener la dimensión de los embeddings.

        Returns:
            1536 para text-embedding-3-small, 3072 para text-embedding-3-large
        """
        return self._dimension

    def get_provider_name(self) -> str:
        """
        Obtener nombre del proveedor.

        Returns:
            "OpenAI"
        """
        return "OpenAI"

    def validate_health(self) -> bool:
        """
        Verificar que OpenAI está disponible.

        Returns:
            True si OpenAI responde correctamente
        """
        try:
            # Hacer un embedding simple para verificar
            test_embedding = self.create_embedding("test")
            return len(test_embedding) == self._dimension
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False

    def _get_model_dimension(self, model: str) -> int:
        """
        Obtener dimensión según el modelo.

        Args:
            model: Nombre del modelo

        Returns:
            Dimensión del embedding
        """
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        
        return dimensions.get(model, 1536)

