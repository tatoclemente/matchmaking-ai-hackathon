"""
Contratos de datos (DTOs) para el servicio de embeddings.

Define las interfaces/modelos para requests y responses de embeddings.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class EmbeddingRequest(BaseModel):
    """
    Request para crear un embedding individual.
    
    Attributes:
        text: Texto a convertir en embedding
        model: Modelo de OpenAI a usar (default: text-embedding-3-small)
    """
    text: str = Field(..., min_length=1, description="Texto a embedear")
    model: str = Field(
        default="text-embedding-3-small",
        description="Modelo de embeddings de OpenAI"
    )

    @validator('text')
    def text_not_empty(cls, v):
        """Validar que el texto no esté vacío después de strip"""
        if not v.strip():
            raise ValueError('El texto no puede estar vacío')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Jugador de pádel categoría SEVENTH, ELO 1520",
                "model": "text-embedding-3-small"
            }
        }


class EmbeddingResponse(BaseModel):
    """
    Response de un embedding creado exitosamente.
    
    Attributes:
        embedding: Vector de floats representando el embedding
        model: Modelo usado para generar el embedding
        dimensions: Número de dimensiones del embedding
    """
    embedding: List[float] = Field(..., description="Vector de embedding")
    model: str = Field(..., description="Modelo usado")
    dimensions: int = Field(..., description="Dimensiones del vector")

    @validator('embedding')
    def embedding_not_empty(cls, v):
        """Validar que el embedding tenga elementos"""
        if not v:
            raise ValueError('El embedding no puede estar vacío')
        return v

    @validator('dimensions')
    def dimensions_match_length(cls, v, values):
        """Validar que dimensions coincida con length del embedding"""
        if 'embedding' in values and v != len(values['embedding']):
            raise ValueError(
                f'Dimensions ({v}) no coincide con longitud del embedding ({len(values["embedding"])})'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "embedding": [0.023, -0.012, 0.045],  # ... 1536 en total
                "model": "text-embedding-3-small",
                "dimensions": 1536
            }
        }


class BatchEmbeddingRequest(BaseModel):
    """
    Request para crear múltiples embeddings en batch.
    
    Attributes:
        texts: Lista de textos a convertir en embeddings
        model: Modelo de OpenAI a usar (default: text-embedding-3-small)
    """
    texts: List[str] = Field(..., min_items=1, description="Textos a embedear")
    model: str = Field(
        default="text-embedding-3-small",
        description="Modelo de embeddings de OpenAI"
    )

    @validator('texts')
    def texts_not_empty(cls, v):
        """Validar que todos los textos tengan contenido"""
        for i, text in enumerate(v):
            if not text.strip():
                raise ValueError(f'El texto en índice {i} está vacío')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "Jugador de pádel categoría SEVENTH",
                    "Partido de pádel en Nueva Córdoba"
                ],
                "model": "text-embedding-3-small"
            }
        }


class BatchEmbeddingResponse(BaseModel):
    """
    Response de múltiples embeddings creados en batch.
    
    Attributes:
        embeddings: Lista de vectores de embeddings
        model: Modelo usado para generar los embeddings
        dimensions: Número de dimensiones de cada embedding
        count: Cantidad de embeddings en el batch
    """
    embeddings: List[List[float]] = Field(..., description="Lista de vectores")
    model: str = Field(..., description="Modelo usado")
    dimensions: int = Field(..., description="Dimensiones por vector")
    count: int = Field(..., description="Cantidad de embeddings")

    @validator('count')
    def count_matches_length(cls, v, values):
        """Validar que count coincida con la cantidad de embeddings"""
        if 'embeddings' in values and v != len(values['embeddings']):
            raise ValueError(
                f'Count ({v}) no coincide con cantidad de embeddings ({len(values["embeddings"])})'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "embeddings": [
                    [0.023, -0.012, 0.045],
                    [0.015, -0.008, 0.032]
                ],
                "model": "text-embedding-3-small",
                "dimensions": 1536,
                "count": 2
            }
        }


class ClientConfig(BaseModel):
    """
    Configuración del cliente de OpenAI.
    
    Attributes:
        api_key: API key de OpenAI
        timeout: Timeout en segundos para requests
        max_retries: Número máximo de reintentos
        model: Modelo por defecto a usar
        max_batch_size: Tamaño máximo de batch permitido
    """
    api_key: str = Field(..., min_length=1, description="API key de OpenAI")
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Timeout en segundos"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Número máximo de reintentos"
    )
    model: str = Field(
        default="text-embedding-3-small",
        description="Modelo por defecto"
    )
    max_batch_size: int = Field(
        default=100,
        ge=1,
        le=2048,
        description="Tamaño máximo de batch"
    )

    @validator('api_key')
    def api_key_format(cls, v):
        """Validar formato básico de API key"""
        if not v.startswith('sk-'):
            raise ValueError('API key debe comenzar con "sk-"')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "api_key": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "timeout": 30,
                "max_retries": 3,
                "model": "text-embedding-3-small",
                "max_batch_size": 100
            }
        }

