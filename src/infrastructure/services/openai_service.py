from typing import List, Dict, Any, Optional
import hashlib
import logging

from src.infrastructure.external.openai_client import openai_client, init_openai_client, OpenAIClient
from src.infrastructure.config import config as infra_config
from src.infrastructure.schema.embedding import (
    EmbeddingRequest,
    EmbeddingResponse,
    BatchEmbeddingRequest,
    BatchEmbeddingResponse,
    ClientConfig,
)

logger = logging.getLogger(__name__)


class OpenAIService:
    """Servicio de alto nivel para generación de embeddings.

    Usa `openai_client` (wrapper low-level) y los schemas definidos en
    `src/schemas/embedding.py` para validar entradas/salidas.

    Implementa un caché local simple (in-memory) para evitar llamadas
    repetidas en corto plazo. El caching es por texto+modelo (sha256).
    """

    DEFAULT_MAX_BATCH_SIZE = 100

    def __init__(self, client: Optional[OpenAIClient] = None, max_batch_size: Optional[int] = None):
        # Intentar usar el client inyectado, sino usar el global
        global openai_client
        self.client: Optional[OpenAIClient] = client or openai_client

        # Si no está inicializado, intentar inicializar desde variables de entorno
        if self.client is None:
            api_key = infra_config.OPENAI_API_KEY
            if not api_key:
                raise RuntimeError(
                    "OpenAI client no inicializado y OPENAI_API_KEY no está establecido en el entorno"
                )

            try:
                cfg = ClientConfig(api_key=api_key)
                # Crear directamente sin usar singleton
                from openai import OpenAI as OpenAISDK
                
                class SimpleOpenAIClient:
                    def __init__(self, sdk_client, model):
                        self._sdk = sdk_client
                        self.model = model
                    
                    def create_embedding(self, text):
                        return self._sdk.embeddings.create(
                            model=self.model, input=text, encoding_format="float"
                        ).data[0].embedding
                    
                    def create_embeddings_batch(self, texts):
                        resp = self._sdk.embeddings.create(
                            model=self.model, input=texts, encoding_format="float"
                        )
                        return [item.embedding for item in resp.data]
                
                sdk_client = OpenAISDK(api_key=cfg.api_key)
                self.client = SimpleOpenAIClient(sdk_client, cfg.model)
            except Exception as e:
                raise RuntimeError(
                    f"Error inicializando OpenAI client: {e}"
                )
            
        self.max_batch_size = max_batch_size or self.DEFAULT_MAX_BATCH_SIZE
        self._cache: Dict[str, List[float]] = {}

    def _cache_key(self, text: str, model: str) -> str:
        h = hashlib.sha256()
        h.update(model.encode('utf-8'))
        h.update(b"::")
        h.update(text.encode('utf-8'))
        return h.hexdigest()

    def generate_embedding(self, text: str, model: Optional[str] = None) -> EmbeddingResponse:
        """Genera embedding para un texto individual.

        Validate input with `EmbeddingRequest`, usa caché y devuelve
        un `EmbeddingResponse`.
        """
        model_to_use = model or getattr(self.client, 'model', 'text-embedding-3-small')
        req = EmbeddingRequest(text=text, model=model_to_use)

        key = self._cache_key(req.text, req.model)
        if key in self._cache:
            embedding = self._cache[key]
            logger.debug("Embedding cache hit for key=%s", key)
        else:
            logger.debug("Embedding cache miss for key=%s; calling client", key)
            assert self.client is not None, "OpenAI client no inicializado"
            embedding = self.client.create_embedding(req.text)
            # store in cache
            self._cache[key] = embedding

        resp = EmbeddingResponse(embedding=embedding, model=req.model, dimensions=len(embedding))
        return resp

    def generate_embeddings_batch(self, texts: List[str], model: Optional[str] = None) -> BatchEmbeddingResponse:
        """Genera embeddings para una lista de textos.

        - Valida con `BatchEmbeddingRequest`
        - Usa caché local por texto
        - Envía al client solo los textos que no estén en caché
        - Soporta chunking si la lista excede `max_batch_size`
        """
        model_to_use = model or getattr(self.client, 'model', 'text-embedding-3-small')
        req = BatchEmbeddingRequest(texts=texts, model=model_to_use)

        all_embeddings: List[List[float]] = []

        # Procesar por chunks
        for start in range(0, len(req.texts), self.max_batch_size):
            chunk = req.texts[start : start + self.max_batch_size]

            # Preparar placeholders y detectar missing
            results_chunk: List[Optional[List[float]]] = [None] * len(chunk)
            missing_texts: List[str] = []
            missing_positions: List[int] = []

            for i, t in enumerate(chunk):
                key = self._cache_key(t, req.model)
                if key in self._cache:
                    results_chunk[i] = self._cache[key]
                else:
                    missing_texts.append(t)
                    missing_positions.append(i)

            # Llamar al cliente solo si hay missing
            if missing_texts:
                logger.debug("Calling client.create_embeddings_batch for %d missing texts", len(missing_texts))
                assert self.client is not None, "OpenAI client no inicializado"
                created = self.client.create_embeddings_batch(missing_texts)

                # Guardar en cache y colocar en results_chunk
                if len(created) != len(missing_texts):
                    logger.warning(
                        "Client returned %d embeddings for %d texts (mismatch)",
                        len(created),
                        len(missing_texts),
                    )

                for idx, emb in enumerate(created):
                    pos = missing_positions[idx]
                    text_at_pos = chunk[pos]
                    key = self._cache_key(text_at_pos, req.model)
                    self._cache[key] = emb
                    results_chunk[pos] = emb

            # Ahora results_chunk no tiene None
            for emb in results_chunk:
                assert emb is not None
                all_embeddings.append(emb)

        resp = BatchEmbeddingResponse(
            embeddings=all_embeddings,
            model=req.model,
            dimensions=len(all_embeddings[0]) if all_embeddings else 0,
            count=len(all_embeddings),
        )

        return resp

    def generate_profile_embedding(self, profile_data: Dict[str, Any]) -> EmbeddingResponse:
        """Genera un embedding para un perfil completo combinando campos.

        Construye un texto representativo del perfil y delega a
        `generate_embedding`.
        """
        parts: List[str] = []

        if profile_data.get('name'):
            parts.append(f"Nombre: {profile_data['name']}")

        if profile_data.get('description'):
            parts.append(f"Descripción: {profile_data['description']}")

        if profile_data.get('skills'):
            skills = profile_data['skills']
            if isinstance(skills, list):
                parts.append(f"Habilidades: {', '.join(map(str, skills))}")
            else:
                parts.append(f"Habilidades: {skills}")

        if profile_data.get('interests'):
            interests = profile_data['interests']
            if isinstance(interests, list):
                parts.append(f"Intereses: {', '.join(map(str, interests))}")
            else:
                parts.append(f"Intereses: {interests}")

        if profile_data.get('experience_level'):
            parts.append(f"Nivel de experiencia: {profile_data['experience_level']}")

        profile_text = ". ".join(parts).strip()

        if not profile_text:
            raise ValueError("No hay datos válidos en profile_data para generar un embedding")

        return self.generate_embedding(profile_text)


# Singleton instance for the service
_openai_service: Optional[OpenAIService] = None

def get_openai_service() -> OpenAIService:
    """Accessor para inyectar en routers sin crear múltiples instancias."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
