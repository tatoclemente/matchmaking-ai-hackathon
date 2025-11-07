"""
Módulo de routers de FastAPI.

Define todos los endpoints de la API REST.
"""

# Importar routers cuando estén implementados
# from .matchmaking import router as matchmaking_router
from . import example

__all__ = [
    "example",
    # "matchmaking_router",
]

