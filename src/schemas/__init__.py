"""
Schemas/DTOs para el proyecto.

Contratos de datos con validaciones usando Pydantic.
"""

from .embedding import (
    EmbeddingRequest,
    EmbeddingResponse,
    BatchEmbeddingRequest,
    BatchEmbeddingResponse,
    ClientConfig
)

__all__ = [
    "EmbeddingRequest",
    "EmbeddingResponse",
    "BatchEmbeddingRequest",
    "BatchEmbeddingResponse",
    "ClientConfig",
]

