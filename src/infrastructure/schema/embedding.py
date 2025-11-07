"""DTOs para el servicio de embeddings (migrados a Pydantic v2)."""

from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class EmbeddingRequest(BaseModel):
    """Request para crear un embedding individual."""
    text: str = Field(..., min_length=1, description="Texto a embedear")
    model: str = Field(default="text-embedding-3-small", description="Modelo de embeddings de OpenAI")

    @field_validator("text")
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El texto no puede estar vacío")
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "text": "Jugador de pádel categoría SEVENTH, ELO 1520",
            "model": "text-embedding-3-small"
        }
    })


class EmbeddingResponse(BaseModel):
    embedding: List[float] = Field(..., description="Vector de embedding")
    model: str = Field(..., description="Modelo usado")
    dimensions: int = Field(..., description="Dimensiones del vector")

    @field_validator("embedding")
    def embedding_not_empty(cls, v: List[float]) -> List[float]:
        if not v:
            raise ValueError("El embedding no puede estar vacío")
        return v

    @model_validator(mode="after")
    def validate_dimensions(self):
        if self.dimensions != len(self.embedding):
            raise ValueError(f"Dimensions ({self.dimensions}) no coincide con longitud del embedding ({len(self.embedding)})")
        return self

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "embedding": [0.023, -0.012, 0.045],
            "model": "text-embedding-3-small",
            "dimensions": 1536
        }
    })


class BatchEmbeddingRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, description="Textos a embedear")
    model: str = Field(default="text-embedding-3-small", description="Modelo de embeddings de OpenAI")

    @field_validator("texts")
    def texts_not_empty(cls, v: List[str]) -> List[str]:
        for i, text in enumerate(v):
            if not text.strip():
                raise ValueError(f"El texto en índice {i} está vacío")
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "texts": [
                "Jugador de pádel categoría SEVENTH",
                "Partido de pádel en Nueva Córdoba"
            ],
            "model": "text-embedding-3-small"
        }
    })


class BatchEmbeddingResponse(BaseModel):
    embeddings: List[List[float]] = Field(..., description="Lista de vectores")
    model: str = Field(..., description="Modelo usado")
    dimensions: int = Field(..., description="Dimensiones por vector")
    count: int = Field(..., description="Cantidad de embeddings")

    @model_validator(mode="after")
    def check_consistency(self):
        if self.count != len(self.embeddings):
            raise ValueError(f"Count ({self.count}) no coincide con cantidad de embeddings ({len(self.embeddings)})")
        return self

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "embeddings": [
                [0.023, -0.012, 0.045],
                [0.015, -0.008, 0.032]
            ],
            "model": "text-embedding-3-small",
            "dimensions": 1536,
            "count": 2
        }
    })


class ClientConfig(BaseModel):
    api_key: str = Field(..., min_length=1, description="API key de OpenAI")
    timeout: int = Field(default=30, ge=1, le=300, description="Timeout en segundos")
    max_retries: int = Field(default=3, ge=0, le=10, description="Número máximo de reintentos")
    model: str = Field(default="text-embedding-3-small", description="Modelo por defecto")
    max_batch_size: int = Field(default=100, ge=1, le=2048, description="Tamaño máximo de batch")

    @field_validator("api_key")
    def api_key_format(cls, v: str) -> str:
        if not v.startswith("sk-"):
            raise ValueError("API key debe comenzar con 'sk-'")
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "api_key": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "timeout": 30,
            "max_retries": 3,
            "model": "text-embedding-3-small",
            "max_batch_size": 100
        }
    })

