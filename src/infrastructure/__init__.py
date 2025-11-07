"""
Módulo de infraestructura.

Contiene toda la capa de infraestructura del proyecto:
- database: Conexión y manejo de base de datos
- external: Clientes para APIs externas (OpenAI, Pinecone, etc.)
- schemas: DTOs y validaciones con Pydantic
- services: Servicios de negocio
- seeders: Scripts para poblar datos
"""

# Re-exportar módulos principales para imports limpios
from .config import config

__all__ = [
    "config",
]

