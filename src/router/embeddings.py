"""Router de embeddings: expone operaciones de OpenAIService.

Endpoints:
- POST /api/embeddings -> embedding individual
- POST /api/embeddings/batch -> embeddings batch
- POST /api/embeddings/profile -> embedding de perfil agregado
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.infrastructure.services.openai_service import get_openai_service
from src.infrastructure.schema.embedding import (
    EmbeddingRequest,
    EmbeddingResponse,
    BatchEmbeddingRequest,
    BatchEmbeddingResponse,
)

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


class ProfileEmbeddingRequest(BaseModel):
    name: Optional[str] = Field(None, description="Nombre del jugador")
    description: Optional[str] = Field(None, description="Descripción del jugador")
    skills: Optional[List[str]] = Field(None, description="Lista de habilidades")
    interests: Optional[List[str]] = Field(None, description="Lista de intereses")
    experience_level: Optional[str] = Field(None, description="Nivel de experiencia")


@router.post(
    "",
    response_model=EmbeddingResponse,
    status_code=status.HTTP_200_OK,
    summary="Generar embedding (single)"
)
async def create_embedding(request: EmbeddingRequest):
    service = get_openai_service()
    try:
        return service.generate_embedding(text=request.text, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando embedding: {e}")


@router.post(
    "/batch",
    response_model=BatchEmbeddingResponse,
    status_code=status.HTTP_200_OK,
    summary="Generar embeddings batch"
)
async def create_embeddings_batch(request: BatchEmbeddingRequest):
    service = get_openai_service()
    try:
        return service.generate_embeddings_batch(texts=request.texts, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando embeddings batch: {e}")


@router.post(
    "/profile",
    response_model=EmbeddingResponse,
    status_code=status.HTTP_200_OK,
    summary="Generar embedding de perfil"
)
async def create_profile_embedding(request: ProfileEmbeddingRequest):
    service = get_openai_service()
    try:
        data: Dict[str, Any] = request.model_dump()
        return service.generate_profile_embedding(profile_data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando embedding de perfil: {e}")
