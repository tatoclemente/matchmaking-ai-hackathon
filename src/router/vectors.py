"""Router de vectores: operaciones sobre PineconeService.

Endpoints:
- POST /api/vectors/upsert -> inserta / actualiza vectores
- POST /api/vectors/search -> busca similares
- DELETE /api/vectors -> borra todos los vectores (opcional namespace)
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from src.infrastructure.services.pinecone_service import get_pinecone_service

router = APIRouter(prefix="/api/vectors", tags=["vectors"])


class VectorItem(BaseModel):
    id: str = Field(..., description="ID único del vector")
    values: List[float] = Field(..., min_length=1, description="Lista de floats del embedding")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata asociada")

    @property
    def dimension(self) -> int:  # pragma: no cover - helper
        return len(self.values)


class UpsertVectorsRequest(BaseModel):
    vectors: List[VectorItem] = Field(..., min_length=1)
    namespace: Optional[str] = Field(None, description="Namespace opcional")


class UpsertVectorsResponse(BaseModel):
    status: str
    count: int
    namespace: Optional[str]


class SearchVectorsRequest(BaseModel):
    vector: List[float] = Field(..., min_length=1, description="Embedding de consulta")
    top_k: Optional[int] = Field(5, ge=1, le=200)
    namespace: Optional[str] = Field(None)
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros metadata Pinecone")


class Match(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any] | None = None

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]):  # pragma: no cover - simple transform
        rid = raw.get("id")
        rscore = raw.get("score")
        if rid is None or rscore is None:
            raise ValueError("Match inválido sin id o score")
        return cls(id=str(rid), score=float(rscore), metadata=raw.get("metadata"))


class SearchVectorsResponse(BaseModel):
    matches: List[Match]
    count: int
    namespace: Optional[str]


class DeleteVectorsResponse(BaseModel):
    status: str
    namespace: Optional[str]


@router.post(
    "/upsert",
    response_model=UpsertVectorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Upsert de vectores"
)
async def upsert_vectors(request: UpsertVectorsRequest):
    service = get_pinecone_service()
    try:
        raw_vectors = [v.model_dump() for v in request.vectors]
        result = service.upsert(vectors=raw_vectors, namespace=request.namespace)
        return UpsertVectorsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en upsert de vectores: {e}")


@router.post(
    "/search",
    response_model=SearchVectorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Búsqueda de vectores similares"
)
async def search_vectors(request: SearchVectorsRequest):
    service = get_pinecone_service()
    try:
        raw = service.search(vector=request.vector, top_k=request.top_k or 5, namespace=request.namespace, filters=request.filters)
        # Transform matches to pydantic objects
        matches = [Match.from_raw(m) for m in raw["matches"]]
        return SearchVectorsResponse(matches=matches, count=len(matches), namespace=raw.get("namespace"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando vectores: {e}")


@router.delete(
    "",
    response_model=DeleteVectorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar todos los vectores"
)
async def delete_vectors(namespace: Optional[str] = Query(None, description="Namespace opcional")):
    service = get_pinecone_service()
    try:
        result = service.delete_all(namespace=namespace)
        return DeleteVectorsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando vectores: {e}")
