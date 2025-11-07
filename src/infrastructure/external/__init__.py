"""
Módulo de servicios externos.

Clientes para comunicación con APIs externas:
- OpenAI: Embeddings
- Pinecone: Vector database (futuro)
- Otros proveedores externos
"""

from .openai_client import OpenAIClient

__all__ = [
    "OpenAIClient",
]

