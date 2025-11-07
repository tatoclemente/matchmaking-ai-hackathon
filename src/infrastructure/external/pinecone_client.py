from typing import List, Dict, Any, Optional
import logging

from pinecone import Pinecone, ServerlessSpec  # type: ignore
from src.infrastructure.config import config
from src.infrastructure.schema.pinecone import PineconeConfig

logger = logging.getLogger(__name__)


class PineconeClient:
    """Cliente Pinecone con patrón singleton similar a OpenAIClient."""

    _instance: Optional["PineconeClient"] = None
    _initialized: bool = False

    def __init__(self, cfg: PineconeConfig):
        if PineconeClient._initialized:
            return
        self.config = cfg
        self.pc: Optional[Pinecone] = None
        self.index = None
        PineconeClient._initialized = True

    @classmethod
    def get_instance(cls, cfg: Optional[PineconeConfig] = None) -> "PineconeClient":
        if cls._instance is None:
            if cfg is None:
                # Auto-init desde variables de entorno si no se provee cfg
                env_cfg = PineconeConfig(
                    api_key=config.PINECONE_API_KEY or "",
                    index_name=config.PINECONE_INDEX_NAME,
                    environment=config.PINECONE_ENVIRONMENT,
                )
                cls._instance = cls(env_cfg)
            else:
                cls._instance = cls(cfg)
        return cls._instance

    def _get_client(self) -> Pinecone:
        if self.pc is None:
            if not self.config.api_key:
                raise RuntimeError("PINECONE_API_KEY no está configurado")
            self.pc = Pinecone(api_key=self.config.api_key)
        return self.pc

    @property
    def index_name(self) -> str:
        return self.config.index_name

    def initialize_index(self):
        pc = self._get_client()
        existing = []
        try:
            existing = pc.list_indexes().names()
        except Exception:
            try:
                existing = [idx["name"] for idx in pc.list_indexes()]
            except Exception:
                pass

        if self.index_name not in existing:
            logger.info("Creando índice Pinecone '%s'", self.index_name)
            try:
                pc.create_index(
                    name=self.index_name,
                    dimension=self.config.dimension,
                    metric=self.config.metric,
                    spec=ServerlessSpec(cloud=self.config.cloud, region=self.config.environment),
                )
            except TypeError:
                pc.create_index(name=self.index_name, dimension=self.config.dimension, metric=self.config.metric)  # type: ignore[call-arg]

        self.index = pc.Index(self.index_name)
        return self.index

    def upsert_vectors(self, vectors: List[Dict[str, Any]], namespace: Optional[str] = None):
        """Inserta o actualiza vectores en el índice.

        Args:
            vectors: Lista de diccionarios con formato {"id": str, "values": List[float], "metadata": {...}}
            namespace: Namespace opcional para segmentar datos.
        """
        if not self.index:
            self.initialize_index()
        assert self.index is not None
        if namespace:
            self.index.upsert(vectors=vectors, namespace=namespace)  # type: ignore[arg-type]
        else:
            self.index.upsert(vectors=vectors)  # type: ignore[arg-type]

    def search_similar(
        self,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 50,
        namespace: Optional[str] = None,
    ):
        """Busca vectores similares.

        Args:
            query_embedding: Embedding de consulta.
            filters: Filtros metadata (dict Pinecone).
            top_k: Número máximo de coincidencias.
            namespace: Namespace opcional.
        """
        if not self.index:
            self.initialize_index()
        assert self.index is not None
        kwargs: Dict[str, Any] = {"vector": query_embedding, "filter": filters, "top_k": top_k, "include_metadata": True}
        if namespace:
            kwargs["namespace"] = namespace
        res = self.index.query(**kwargs)
        return res.matches  # type: ignore[attr-defined]

    def delete_all_vectors(self, namespace: Optional[str] = None):
        """Elimina todos los vectores del índice (opcionalmente dentro de un namespace)."""
        if not self.index:
            self.initialize_index()
        assert self.index is not None
        if namespace:
            self.index.delete(delete_all=True, namespace=namespace)
        else:
            self.index.delete(delete_all=True)


pinecone_client: Optional[PineconeClient] = None


def init_pinecone_client(cfg: Optional[PineconeConfig] = None) -> PineconeClient:
    global pinecone_client
    pinecone_client = PineconeClient.get_instance(cfg)
    logger.info("PineconeClient inicializado con índice=%s", pinecone_client.index_name)
    return pinecone_client
