"""
Mock Provider para Testing del Embedding Service.

Este mock permite testear sin hacer llamadas reales a OpenAI API.
"""

from typing import List
from src.external.embedding_provider import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Mock provider que retorna embeddings fake sin llamar a APIs externas.
    
    Útil para:
    - Unit tests
    - Integration tests que no necesitan embeddings reales
    - CI/CD donde no quieres gastar en API calls
    """

    def __init__(self, dimension: int = 1536, fixed_value: float = 0.1):
        """
        Inicializar mock provider.

        Args:
            dimension: Dimensión de los embeddings (default: 1536 para OpenAI)
            fixed_value: Valor para llenar el vector (default: 0.1)
        """
        self.dimension = dimension
        self.fixed_value = fixed_value
        self.call_count = 0  # Para verificar en tests
        self.last_texts = []  # Para debugging

    def create_embedding(self, text: str) -> List[float]:
        """
        Crear embedding fake.

        Args:
            text: Texto (se ignora, solo para logging)

        Returns:
            Vector fake de self.dimension elementos
        """
        self.call_count += 1
        self.last_texts.append(text)
        
        # Retornar vector fake
        return [self.fixed_value] * self.dimension

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Crear batch de embeddings fake.

        Args:
            texts: Lista de textos

        Returns:
            Lista de vectores fake
        """
        self.call_count += len(texts)
        self.last_texts.extend(texts)
        
        # Retornar batch de vectores fake
        return [[self.fixed_value] * self.dimension for _ in texts]

    def get_embedding_dimension(self) -> int:
        """Retornar dimensión configurada."""
        return self.dimension

    def get_provider_name(self) -> str:
        """Retornar nombre del mock."""
        return "MockProvider"

    def validate_health(self) -> bool:
        """Mock siempre está 'healthy'."""
        return True

    # Métodos útiles para testing
    def reset(self):
        """Resetear counters (útil entre tests)."""
        self.call_count = 0
        self.last_texts = []

    def get_call_count(self) -> int:
        """Obtener número de llamadas realizadas."""
        return self.call_count

    def get_last_text(self) -> str:
        """Obtener último texto procesado."""
        return self.last_texts[-1] if self.last_texts else ""

    def get_all_texts(self) -> List[str]:
        """Obtener todos los textos procesados."""
        return self.last_texts.copy()


class DeterministicMockProvider(EmbeddingProvider):
    """
    Mock provider que retorna embeddings únicos basados en el texto.
    
    Útil para tests que necesitan embeddings diferentes para textos diferentes.
    """

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def create_embedding(self, text: str) -> List[float]:
        """
        Crear embedding determinístico basado en hash del texto.

        Args:
            text: Texto de entrada

        Returns:
            Vector único para este texto
        """
        # Usar hash del texto para generar valores únicos pero determinísticos
        hash_value = hash(text)
        
        # Generar vector basado en el hash
        embedding = []
        for i in range(self.dimension):
            # Combinar hash con índice para generar valor único
            value = ((hash_value + i) % 1000) / 1000.0
            embedding.append(value)
        
        return embedding

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Crear batch de embeddings determinísticos."""
        return [self.create_embedding(text) for text in texts]

    def get_embedding_dimension(self) -> int:
        return self.dimension

    def get_provider_name(self) -> str:
        return "DeterministicMockProvider"

    def validate_health(self) -> bool:
        return True

