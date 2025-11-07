"""Esquema de configuración para el cliente de Pinecone (Pydantic v2)."""
from pydantic import BaseModel, Field, field_validator, ConfigDict


class PineconeConfig(BaseModel):
    api_key: str = Field(..., min_length=1, description="API key de Pinecone")
    index_name: str = Field(default="matchmaking-players", min_length=1)
    environment: str = Field(default="us-east-1", min_length=1, description="Región serverless")
    dimension: int = Field(default=1536, ge=1, le=16384)
    metric: str = Field(default="cosine")
    cloud: str = Field(default="aws")

    @field_validator("api_key")
    def api_key_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Pinecone API key no puede ser vacía")
        return v

    @field_validator("metric")
    def metric_supported(cls, v: str) -> str:
        allowed = {"cosine", "dotproduct", "euclidean"}
        if v not in allowed:
            raise ValueError(f"Métrica no soportada: {v}. Permitidas: {', '.join(sorted(allowed))}")
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "api_key": "pc-test-xxxx",
            "index_name": "matchmaking-players",
            "environment": "us-east-1",
            "dimension": 1536,
            "metric": "cosine",
            "cloud": "aws"
        }
    })
