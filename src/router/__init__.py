"""
Módulo de routers de FastAPI.

Define todos los endpoints de la API REST.
"""

from .matchmaking import router as matchmaking_router

__all__ = [
    "matchmaking_router",
]

