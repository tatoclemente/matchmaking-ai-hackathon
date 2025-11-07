"""
Módulo de servicios de negocio.

Contiene la lógica de aplicación y orquestación de servicios externos.
"""

from .openai_service import OpenAIService

__all__ = [
    "OpenAIService",
]
