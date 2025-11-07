from typing import List, Optional, Dict, Any

from src.infrastructure.external.pinecone_client import (
    pinecone_client,
    init_pinecone_client,
    PineconeClient,
)


class PineconeService:
    """Servicio de alto nivel sobre PineconeClient para desacoplar routers.

    Responsabilidades:
    - Asegurar inicialización del cliente / índice.
    - Proveer métodos semánticos (upsert/search/delete_all).
    - Normalizar estructura de respuesta.
    Nota: Operaciones soportan namespaces opcionales.
    """

    def __init__(self, client: Optional[PineconeClient] = None):
        self._client = client or pinecone_client

    def _ensure_client(self) -> PineconeClient:
        if self._client is None:
            self._client = init_pinecone_client()
        return self._client

    def upsert(self, vectors: List[Dict[str, Any]], namespace: Optional[str] = None) -> Dict[str, Any]:
        client = self._ensure_client()
        client.upsert_vectors(vectors=vectors, namespace=namespace)
        return {"status": "ok", "count": len(vectors), "namespace": namespace}

    def search(self, vector: List[float], top_k: int = 5, namespace: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        client = self._ensure_client()
        matches = client.search_similar(query_embedding=vector, top_k=top_k, namespace=namespace, filters=filters)
        return {"matches": matches, "count": len(matches), "namespace": namespace}

    def delete_all(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        client = self._ensure_client()
        client.delete_all_vectors(namespace=namespace)
        return {"status": "ok", "namespace": namespace}


_pinecone_service: Optional[PineconeService] = None

def get_pinecone_service() -> PineconeService:
    global _pinecone_service
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    return _pinecone_service
