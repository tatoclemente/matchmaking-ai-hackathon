from openai import OpenAI
from typing import List, Optional, Union
import logging

from src.infrastructure.schema.embedding import (
    EmbeddingRequest,
    BatchEmbeddingRequest,
    ClientConfig,
)

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Wrapper low-level del SDK de OpenAI.

    Inicializable con `ClientConfig`. Uso recomendado:
        OpenAIClient.get_instance(config)

    También se provee `init_openai_client(config)` que guarda una
    referencia global `openai_client` para importación directa.
    """

    _instance: Optional['OpenAIClient'] = None
    _initialized: bool = False

    def __init__(self, config: ClientConfig):
        if OpenAIClient._initialized:
            return

        self.config = config
        # Inicializar cliente del SDK
        self._client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model
        self.timeout = self.config.timeout
        self.max_retries = self.config.max_retries
        self.max_batch_size = self.config.max_batch_size

        OpenAIClient._initialized = True

    @classmethod
    def get_instance(cls, config: Optional[ClientConfig] = None) -> 'OpenAIClient':
        """Obtener la instancia singleton. Si no existe, requiere `config`."""
        if cls._instance is None:
            if config is None:
                raise ValueError("OpenAIClient no inicializado. Proveer ClientConfig en la primera llamada.")
            cls._instance = cls(config)
        return cls._instance

    def _sdk_client(self) -> OpenAI:
        return self._client

    def create_embedding(self, request: Union[str, EmbeddingRequest]) -> List[float]:
        """Crear embedding para un texto.

        Acepta un `EmbeddingRequest` o un `str` (texto). Devuelve la lista de floats.
        """
        if isinstance(request, str):
            req = EmbeddingRequest(text=request, model=self.model)
        else:
            req = request

        # Llamada al SDK
        resp = self._sdk_client().embeddings.create(
            model=req.model,
            input=req.text,
            encoding_format="float",
        )

        return resp.data[0].embedding

    def create_embeddings_batch(self, request: Union[List[str], BatchEmbeddingRequest]) -> List[List[float]]:
        """Crear embeddings en batch.

        Acepta una lista de textos o un `BatchEmbeddingRequest`. Respeta `max_batch_size`.
        """
        if isinstance(request, list):
            req = BatchEmbeddingRequest(texts=request, model=self.model)
        else:
            req = request

        texts = req.texts
        if len(texts) > self.max_batch_size:
            # Dividir en trozos y concatenar resultados
            results: List[List[float]] = []
            for start in range(0, len(texts), self.max_batch_size):
                chunk = texts[start : start + self.max_batch_size]
                results.extend(self.create_embeddings_batch(BatchEmbeddingRequest(texts=chunk, model=req.model)))
            return results

        resp = self._sdk_client().embeddings.create(
            model=req.model,
            input=texts,
            encoding_format="float",
        )

        return [item.embedding for item in resp.data]


# Helper global: init y referencia
openai_client: Optional[OpenAIClient] = None


def init_openai_client(config: ClientConfig) -> OpenAIClient:
    """Inicializa y devuelve la instancia singleton; guarda en `openai_client` global."""
    global openai_client
    openai_client = OpenAIClient.get_instance(config)
    logger.info("OpenAIClient inicializado con modelo=%s", config.model)
    return openai_client

